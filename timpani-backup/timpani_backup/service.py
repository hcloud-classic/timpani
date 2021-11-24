import threading
import time
import platform
import datetime
import timpani_backup.constants
import requests
import json
from timpani_apimanager.process.status.backup import BackupStatus
from timpani_apimanager.process.status.restore import RestoreStatus
from nameko.rpc import rpc
from nameko.timer import timer

from timpani_backup.configuration.configuration_file_reader import ConfigrationFileReader
from timpani_backup.configuration.config_set import ConfigSetting
from timpani_backup.configuration.register_service import RegisterService
from timpani_backup.transfer import TransferServiceManager
from . import worker_th
from . import metadata
import copy
import sys
from .models.backupdata import BackupData
from .module.zvolmetadata import zvolMetaData
from .module.backupstorage import BackupStorage
from .module.snapshot import Snapshot
from .module.snapshotrestore import SnapshotRestore
from .util.systemutil import Systemutil
from .models.restoreproc import RestoreProc
from .module.rsyncmetadata import RsyncMetaData
from .module.rsync import RsyncRun
from .module.iscsi import IscsiProc


import logging.handlers
################################### logger ############################################################################
logger = logging.getLogger(__name__)
#logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
fileHandler = logging.handlers.TimedRotatingFileHandler(filename='./log_'+__name__.__str__(), when='midnight', backupCount=0, interval=1, encoding='utf-8')
fileHandler.setFormatter(formatter)
fileHandler.setLevel(level=logging.INFO)
logger.addHandler(fileHandler)
# stream_hander = logging.StreamHandler()
# stream_hander.setFormatter(formatter)
# stream_hander.setLevel(level=logging.INFO)
# logger.addHandler(stream_hander)
#######################################################################################################################

class ServiceInit(object):

    def __init__(self):
        import timpani_backup.constants
        config = ConfigrationFileReader()
        config_set = ConfigSetting(config.read_file())
        config_set.setConfig()
        self.service_manager_trans = TransferServiceManager(timpani_backup.constants.AMQP_CONFIG)
        service_data = RegisterService(node_uuid=timpani_backup.constants.NODE_UUID,
                                   capability=timpani_backup.constants.CAPABILITY,
                                   ipv4address=timpani_backup.constants.SERVICE_IPV4ADDR)

        # get Agent ID
        res_data = self.service_manager_trans.send(method="registerService", service_name='service_manager' ,msg=service_data.__dict__)
        if 'agent_id' in res_data.keys():
            timpani_backup.constants.AGENT_ID = res_data.get('agent_id')
        else:
            logger.debug("GET Agent KEY FAILED")
            exit()

        self.node_uuid = timpani_backup.constants.NODE_UUID
        self.agent_id = timpani_backup.constants.AGENT_ID
        self.address = timpani_backup.constants.SERVICE_IPV4ADDR
        self.remote_path_base = timpani_backup.constants.REMOTE_PATH_BASE
        self.backup_host = timpani_backup.constants.BACKUP_SERVER_HOST
        self.amqp_url = timpani_backup.constants.AMQP_CONFIG
        self.service_name = "{}_service_{}".format(timpani_backup.constants.CAPABILITY, timpani_backup.constants.NODE_UUID)

    def service_send(self, method, msg):
        ret = self.service_manager_trans.send(method=method, service_name='service_manager', msg=msg)
        return ret

class RestAppService(object):

    systemutil = Systemutil()
    config = ConfigrationFileReader()

    def __init__(self, moduletype):
        self.nodetype_url = "/v1/app/nodetype"
        self.addservice_url = "/v1/app/addservice"
        self.keepalive_url = "/v1/app/keepalive"
        self.checkdir_url = "/v1/app/checkdir"
        config = self.config.read_file()
        self.backup_host = config['GENERAL']['BACKUP_IP']
        self.backup_webport = config['GENERAL']['WEBPORT']
        self.node_uuid = None
        self.amqp_url = None
        self.nodetype = None
        self.prefix = None
        self.nicname = None
        self.moduletype = moduletype


    def rest_request(self, url, postdata):
        issuccess = False
        resdata = None
        try:
            response = requests.post(url, data=json.dumps(postdata), timeout=3)
            if response.status_code == 200:
                logger.info("response data : {}".format(response.json()['resultData']))
                resdata = response.json()['resultData']
                issuccess = True
                if 'errorcode' in resdata:
                    logger.info("Get Nodetype Faild")
                    issuccess = False
            else:
                logger.info("response data : {}".format(response))
        except Exception as e:
            logger.info("api gateway connection failed : {}".format(e))

        return issuccess, resdata

    def getnodetype(self):
        home_url = "http://{host}:{port}".format(host=self.backup_host, port=self.backup_webport)
        self.uuid = self.systemutil.getSystemUuid()
        postdata = {'node_uuid': self.uuid}
        url = home_url + self.nodetype_url
        issuccess, resdata = self.rest_request(url, postdata)
        if issuccess:
            self.nodetype = resdata.get('nodetype')
            self.prefix = resdata.get('configdata').get('prefix')
            self.nicname = resdata.get('configdata').get('nicname')
            config_data_rabbit_id = resdata.get('configdata').get('rabbit_id')
            config_data_rabbit_pass = resdata.get('configdata').get('rabbit_pass')
            config_data_rabbit_port = resdata.get('configdata').get('rabbit_port')
            self.amqp_url = "amqp://{id}:{passwd}@{host}:{port}".\
                format(id=config_data_rabbit_id, passwd=config_data_rabbit_pass,
                       host=self.backup_host, port=config_data_rabbit_port)
        return issuccess

    def addservice(self):
        home_url = "http://{host}:{port}".format(host=self.backup_host, port=self.backup_webport)
        ipaddress = self.systemutil.getIpAddress(self.nicname)
        self.pid = self.systemutil.getPid()
        macaddress = self.systemutil.getMacAddress(self.nicname)
        postdata = {'node_uuid': self.uuid, 'pid': self.pid, 'nodetype':self.nodetype,
                    'ipaddress': ipaddress, 'macaddress': macaddress,
                    'moduletype': self.moduletype}
        url = home_url + self.addservice_url
        issuccess, resdata = self.rest_request(url, postdata)
        if issuccess:
            self.modulename = resdata.get('modulename')
        return issuccess

    def keepalive(self):
        home_url = "http://{host}:{port}".format(host=self.backup_host, port=self.backup_webport)
        postdata = {'pid': self.pid, 'moduletype': self.moduletype}
        url = home_url + self.keepalive_url
        issuccess, resdata = self.rest_request(url, postdata)
        # if issuccess:
        #     self.modulename = resdata.get('modulename')
        return issuccess

    def checkdatadir(self):
        modulename = self.modulename
        uuid = self.uuid
        prefix = self.prefix
        meta = RsyncMetaData()
        if platform.system() == 'FreeBSD':
            post_data = meta.freebsddatadir(prefix, uuid, modulename)
        else:
            post_data = meta.linuxdatadir(prefix, uuid, modulename)

        home_url = "http://{host}:{port}".format(host=self.backup_host, port=self.backup_webport)
        postdata = {'postdata': post_data}
        url = home_url + self.checkdir_url
        issuccess, resdata = self.rest_request(url, postdata)
        # if issuccess:
        #     self.modulename = resdata.get('modulename')
        return issuccess


class BackupService(object):
    max_retry = 60
    init_data = RestAppService(moduletype='backup')
    retry_cnt = 0
    while True:
        if not init_data.getnodetype():
            logger.info("MODULE SERVICE REGITER FAILED")
        else:
            break

        if retry_cnt == max_retry:
            logger.info("MODULE SERVICE REGITER RETRY FAILED")
            sys.exit()
        time.sleep(1)
        retry_cnt += 1

    retry_cnt = 0
    while True:
        if not init_data.addservice():
            logger.info("MODULE SERVICE REGITER FAILED")
        else:
            break
        if retry_cnt == max_retry:
            logger.info("MODULE SERVICE REGITER RETRY FAILED")
            sys.exit()
        time.sleep(1)
        retry_cnt += 1
    name = init_data.modulename
    node_uuid = init_data.node_uuid
    # agent_id = init_data.agent_id
    # ip_address = init_data.address
    # send_service = init_data.service_send
    # remote_path_base = init_data.remote_path_base
    backup_host = init_data.backup_host
    amqp_url = init_data.amqp_url
    logger.debug("name : {}, node_uuid : {}".format(__name__, node_uuid))

    @timer(interval=30)
    def keepalive(self):
        logger.debug("START KEEPALIVE")
        self.init_data.keepalive()

    @rpc
    def backupproc(self, data):

        proc = data.get('proc')
        backupstorage = BackupStorage()
        dataset = data.get('name')

        if proc.__eq__(BackupStatus.ZVOLMETADATACOLLECT.value[0]):
            meta = zvolMetaData(dataset, True)
            logger.info("zvol meta data collection")
            cur_collectdata = meta.collect_zfs()
            iscsi = IscsiProc()
            data = iscsi.iscsiinfo(data)
            data['cur_collectdata'] = cur_collectdata
        elif proc.__eq__(BackupStatus.SNAPSHOTCREATE_FULL.value[0]):
            logger.info("snapshot create [full]")
            snapshot = Snapshot()
            cur_snaplist = data.get('cur_collectdata').get('cur_snaplist')
            snapshot.destorysnapshotall(cur_snaplist)
            snapshot.createsnapshot(data)
        elif proc.__eq__(BackupStatus.SNAPSHOTCREATE.value[0]):
            logger.info("snapshot create")
            snapshot = Snapshot()
            usetype = data.get('usetype')
            nodetype = data.get('nodetype')
            cur_snaplist = data.get('cur_collectdata').get('cur_snaplist')
            data['priv_snapfullname'] = None
            data['priv_snapfilename'] = None
            if data.get('dbmetadata') is None:
                # All Snapshot Destroy
                snapshot.destorysnapshotall(cur_snaplist)
            elif nodetype.__eq__('COMPUTE'):
                # 'snapdata', zfspropertys, bootdata, pooldata, poolpropertys
                priv_snapdata = data.get('dbmetadata').get('snapdata')
                if priv_snapdata is not None:
                    data['priv_snapfullname'] = priv_snapdata.get('snapfullname')
                    data['priv_snapfilename'] = priv_snapdata.get('snapfilename')
                    logger.info('cur_snaplist : {}'.format(cur_snaplist))
                    snapshot_check_ok = 0
                    for snapdata in cur_snaplist:
                        isnotdestroy = True
                        index_cnt = snapdata.get('index')
                        snapshotname = snapdata.get('zfs_name')
                        if snapshotname.__eq__(data.get('priv_snapfullname')):
                            isnotdestroy = False
                            if index_cnt == 1:
                                snapshot_check_ok = 1
                            else:
                                snapshot_check_ok = 2

                        if isnotdestroy:
                            snapshot.destorysnapshot_one(snapshotname)

            logger.info('priv_snapfullname : {}'.format(data.get('priv_snapfullname')))
            logger.info('priv_snapfilename : {}'.format(data.get('priv_snapfilename')))
            snapshot.createsnapshot(data)
        elif proc.__eq__(BackupStatus.SNAPSHOTMETADATACOLLECT.value[0]):
            logger.info("snapshot meta data collection")

            meta = zvolMetaData(dataset, True)
            snaplist, snapcnt = meta.cur_snaplist()
            data['check_snaplist'] = snaplist
            devlist = data.get('cur_collectdata').get('cur_devlist')
            osname = data.get('cur_collectdata').get('osname')
            logger.info("devlist : {}, osname : {}, part_path : {}".format(devlist, osname, data.get('part_path')))
            savepath = data.get('part_path').get('save_part')
            if savepath is None:
                logger.info('Part Save Path None')
            else:
                logger.info("devlist : {}, osname : {}, part_path : {}".format(devlist, osname, savepath))
                meta.save_partitioninfo(osname, devlist, savepath)
        elif proc.__eq__(BackupStatus.SNAPSHOTDESTROY.value[0]):
            logger.info("snapshot destory")
            snapshot = Snapshot()
            snapshot.destorysnapshot(data, False)
        elif proc.__eq__(BackupStatus.SNAPSHOTDESTROY_FULL.value[0]):
            logger.info("snapshot destory")
            snapshot = Snapshot()
            snapshot.destorysnapshot(data, True)
        elif proc.__eq__(BackupStatus.NFSMOUNT.value[0]):
            logger.info("nfs mount")
            nfs_server = data.get('nfs_server')
            export_path = data.get('export_path')
            mount_path = data.get('mount_path')
            divicelist, ismount = backupstorage.nfsmount(nfs_server, export_path, mount_path)
            data['nfs'] = {'divicelist': divicelist, 'isnfsmount': ismount}
        elif proc.__eq__(BackupStatus.NFSUNMOUNT.value[0]):
            logger.info("nfs unmount")
            nfs_server = data.get('nfs_server')
            export_path = data.get('export_path')
            mount_path = data.get('mount_path')
            ismount = backupstorage.nfsunmount(nfs_server, export_path, mount_path)
            data['nfs']['isnfsmount'] = ismount
        elif proc.__eq__(BackupStatus.METADATAUPDATE.value[0]):
            logger.info("meta data update")
        elif proc.__eq__(BackupStatus.RSYNCMETACOLLECT.value[0]):
            meta = RsyncMetaData()
            data = meta.matadatacollect(data)
        elif proc.__eq__(BackupStatus.RSYNCOSBACKUP.value[0]):
            run = RsyncRun()
            res=run.rsyncosbackup(data)
            if 'error_code' in res:
                return res
            data['snapdata'] = res
        elif proc.__eq__(BackupStatus.RSYNCDATABACKUP.value[0]):
            run = RsyncRun()
            res = run.rsyncdatabackup(data)
            if 'error_code' in res:
                return res
            data['snapdata'] = res
        else:
            logger.info("not found proc : {}".format(proc))

        return data

class RestoreService(object):
    max_retry = 60
    init_data = RestAppService(moduletype='restore')
    retry_cnt = 0
    while True:
        if not init_data.getnodetype():
            logger.info("MODULE SERVICE REGITER FAILED")
        else:
            break

        if retry_cnt == max_retry:
            logger.info("MODULE SERVICE REGITER RETRY FAILED")
            sys.exit()
        time.sleep(1)
        retry_cnt += 1

    retry_cnt = 0
    while True:
        if not init_data.addservice():
            logger.info("MODULE SERVICE REGITER FAILED")
        else:
            break
        if retry_cnt == max_retry:
            logger.info("MODULE SERVICE REGITER RETRY FAILED")
            sys.exit()
        time.sleep(1)
        retry_cnt += 1
    name = init_data.modulename
    node_uuid = init_data.node_uuid
    # agent_id = init_data.agent_id
    # ip_address = init_data.address
    # send_service = init_data.service_send
    # remote_path_base = init_data.remote_path_base
    backup_host = init_data.backup_host
    amqp_url = init_data.amqp_url
    logger.debug("name : {}, node_uuid : {}".format(__name__, node_uuid))

    @timer(interval=30)
    def keepalive(self):
        logger.debug("START KEEPALIVE")
        self.init_data.keepalive()

    @timer(interval=60)
    def checkdatadir(self):
        self.init_data.checkdatadir()

    @rpc
    def restoreproc(self, data):
        restore = RestoreProc()
        proc = data.get('proc')
        dataset = data.get('name')

        if proc.__eq__(RestoreStatus.NFSMOUNT.value[0]):
            logger.info("proc : {}".format(proc))
            data = restore.nfsmount(data)
        elif proc.__eq__(RestoreStatus.NFSUNMOUNT.value[0]):
            logger.info("proc : {}".format(proc))
            data = restore.nfsunmount(data)
        elif proc.__eq__(RestoreStatus.ZVOLMETADATACOLLECT.value[0]):
            logger.info("proc : {}".format(proc))
            data = restore.zvolmetadatacollect(data)
            iscsi = IscsiProc()
            data = iscsi.iscsiinfo(data)
        elif proc.__eq__(RestoreStatus.METADATACOMPARE.value[0]):
            logger.info("proc : {}".format(proc))
        elif proc.__eq__(RestoreStatus.ISCSIDEMONCHECK.value[0]):
            logger.info("proc : {}".format(proc))
            data = restore.iscsidemoncheck(data)
        elif proc.__eq__(RestoreStatus.ISCSIREQUNMOUNT.value[0]):
            logger.info("proc : {}".format(proc))
            data = restore.iscsirequnmount(data)
        elif proc.__eq__(RestoreStatus.ISCSILUNINFODEL.value[0]):
            logger.info("proc : {}".format(proc))
            data = restore.iscsiluninfodel(data)
        elif proc.__eq__(RestoreStatus.SNAPSHOTRESTORE.value[0]):
            logger.info("proc : {}".format(proc))
            # Recover List Check
            # data['restoredata'] = restoredata -> restorelist -> snapinfo
            restore_list = data.get('restoredata').get('restorelist')
            restoresnap = SnapshotRestore()
            check_ok, check_list = restoresnap.checkrestorelist(restore_list)
            logger.info("Check Restore List : {}\n".format(check_ok))
            logger.info("Check Restore List DATA : {}\n".format(check_list))
            if check_ok:
                data['check_list'] = check_list
            data = restore.snapshotrestore(data)
        elif proc.__eq__(RestoreStatus.SNAPSHOTRESTORE_FULL.value[0]):
            logger.info("proc : {} dataset : {}".format(proc, dataset))
            snapshot = Snapshot()
            if dataset is None:
                dataset = data.get('restoredata').get('target_snapdata').get('snapdata').get('dataset')
            meta = zvolMetaData(dataset, True)
            cur_snaplist, _ = meta.cur_snaplist(True)
            logger.info("SNAP LIST : {}".format(cur_snaplist))
            if cur_snaplist is not None:
                for snapdata in cur_snaplist:
                    snapshotname = snapdata.get('zfs_name')
                    snapshot.destorysnapshot_one(snapshotname)

            data = restore.snapshotrestorefull(data)

        elif proc.__eq__(RestoreStatus.ISCSILUNINFOADD.value[0]):
            logger.info("proc : {}".format(proc))
            data = restore.iscsiluninfoadd(data)
        elif proc.__eq__(RestoreStatus.ISCSIREQMOUNT.value[0]):
            logger.info("proc : {}".format(proc))
            data = restore.iscsireqmount(data)
        elif proc.__eq__(RestoreStatus.DATASETRENAME.value[0]):
            # Rollback Data Make
            data = restore.datasetrename(data)
            logger.info("datasetrename DATA : {}\n".format(data.get('restoredata')))
            logger.info("proc : {}".format(proc))

        elif proc.__eq__(RestoreStatus.RENAMEDATADEL.value[0]):
            # Rollback Data Remove
            logger.info("proc : {}".format(proc))
            data = restore.renamedatadel(data)

        elif proc.__eq__(RestoreStatus.RSYNCOSRESTORE.value[0]):
            run = RsyncRun()
            data = run.rsyncosrestore(data)
            # if 'error_code' in res:
            #     return res
            # data['snapdata'] = res
        elif proc.__eq__(RestoreStatus.RSYNCDATARESTORE.value[0]):
            restore_list = data.get('restoredata').get('restorelist')
            restoresnap = SnapshotRestore()
            check_ok, check_list = restoresnap.checkrestorelist(restore_list)
            logger.info("Check Restore List : {}\n".format(check_ok))
            logger.info("Check Restore List DATA : {}\n".format(check_list))
            if check_ok:
                data['check_list'] = check_list

            run = RsyncRun()
            data = run.rsyncdatarestore(data)
            # if 'error_code' in res:
            #     return res
            # data['snapdata'] = res
        else:
            logger.info("not found proc : {}".format(proc))

        return data
