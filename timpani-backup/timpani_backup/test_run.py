from timpani_backup.resource import ResourceSystem
from .module.zvolmetadata import zvolMetaData
from .module.backupstorage import BackupStorage
from .module.snapshot import Snapshot
from .util.systemutil import Systemutil
import json
import sys
import requests
import logging.handlers
################################### logger ############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
# fileHandler = logging.handlers.TimedRotatingFileHandler(filename='./log_'+__name__.__str__(), when='midnight', backupCount=0, interval=1, encoding='utf-8')
# fileHandler.setFormatter(formatter)
# fileHandler.setLevel(level=logging.INFO)
# logger.addHandler(fileHandler)
stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
stream_hander.setLevel(level=logging.INFO)
logger.addHandler(stream_hander)
#######################################################################################################################

class Test(object):

    systemutil = Systemutil()

    def SnapshotTest(self, dataset):

        res = ResourceSystem.Snapshot(dataset=dataset, snapname="sanp_test", recursive=False)
        if res is not None:
            for start_dataset, dataset_name, target_snapname, snap_target, createtime in res:
                print("Snapshot Create Result : \nstart_dataset : {} \ndataset_name : {} \ntarget_snapname : {] \nsnap_target : {} \ncreatetime : {}\n"
                  .format(start_dataset, dataset_name, target_snapname, snap_target, createtime))
        snap_name = "{}@{}".format(dataset, "snap_test")
        res = ResourceSystem.DestorySnapshot(snap_name)
        print("Snapshot Destroy Result : {}".format(res))

    def ModuleInit(self):
        home_url = "http://192.168.221.202:50080"
        net_if_name = "ens33"
        uuid = self.systemutil.getSystemUuid()
        ipaddress = self.systemutil.getIpAddress(net_if_name)
        pid = self.systemutil.getPid()
        macaddress = self.systemutil.getMacAddress(net_if_name)

        logger.info("============ system collect info ===============\n uuid : {}\n pid:{} ipaddress : {}\n macaddress : {}".format(uuid,pid,ipaddress,macaddress))
        nodetype_url = "/v1/app/nodetype"
        nodetype_data = {'node_uuid' : uuid}
        url = home_url + nodetype_url
        response = requests.post(url, data=json.dumps(nodetype_data), timeout = 3)
        if response.status_code == 200:
            logger.info("response data : {}".format(response.json()['resultData']))
            resdata = response.json()['resultData']
            if 'errorcode' in resdata:
                logger.info("Get Nodetype Faild")
                sys.exit()
            nodetype = resdata.get('nodetype')
            config_data_prefix = resdata.get('configdata').get('prefix')
            config_data_nicname = resdata.get('configdata').get('nicname')
            config_data_rabbit_id = resdata.get('configdata').get('rabbit_id')
            config_data_rabbit_pass = resdata.get('configdata').get('rabbit_pass')
            config_data_rabbit_port = resdata.get('configdata').get('rabbit_port')
        else:
            logger.info("[Failed] response data : {}".format(response))

        addservice_url = "/v1/app/addservice"
        addservice_data = {'node_uuid': uuid, 'pid':pid, 'nodetype':nodetype,
                           'ipaddress':ipaddress, 'macaddress': macaddress,
                           'moduletype':'backuptest'}
        url = home_url + addservice_url
        response = requests.post(url, data=json.dumps(addservice_data), timeout=3)
        if response.status_code == 200:
            logger.info("response data : {}".format(response.json()['resultData']))
            resdata = response.json()['resultData']
            modulename = resdata.get('modulename')
        else:
            logger.info("[Failed] response data : {}".format(response))

    def TestZvolMetadata(self, dataset):
        print("TESTZVOL")
        logger.info("INFO TESTZVOL")
        data = {'uuid': '9F824D56-56C1-C83B-5199-1D1DDCB8D5C1', 'usetype': 'DATA', 'nodetype': 'COMPUTE',
                'name': 'hcc'}
        target_uuid = '9F824D5656C1C83B51991D1DDCB8D5C1'
        data['target_uuid'] = target_uuid
        data['server_uuid'] = target_uuid
        meta = zvolMetaData(dataset, True)
        cur_collect = meta.collect_zfs()
        data['cur_collectdata'] = cur_collect
        logger.info("cur_collect : {}".format(data))

        logger.info("======================== [ NFS TEST ] ============================")
        snapshot = Snapshot()
        storage = BackupStorage()
        nfs_server = "192.168.221.202"
        export_path = "/nfsroot"
        mount_path = "/backupstorage"
        data['nfs'] = {'nfs_server': nfs_server, 'export_path':'/nfsroot', 'mount_path':'/backupstorage'}
        storage.nfsmount(nfs_server, export_path, mount_path)
        snapshot.createsnapshot(data)
        snaplist, snapcnt = meta.cur_snaplist()
        data['check_snaplist'] = snaplist
        snapshot.destorysnapshot(data, False)
        storage.nfsunmount(nfs_server, export_path, mount_path)

        logger.info("save data SNAP META: {}".format(data.get('save_snap_meta')))
        logger.info("save data POOL META: {}".format(data.get('cur_pool')))

if __name__=="__main__":
    testsuit = Test()
    dataset = "hcc"
    # testsuit.SnapshotTest(dataset)
    # testsuit.TestZvolMetadata(dataset)
    testsuit.ModuleInit()

