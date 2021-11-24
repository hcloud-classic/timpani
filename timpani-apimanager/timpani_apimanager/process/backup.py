import logging
from .status.backup import BackupStatus
from .worker import BackupWorker
from ..trans.translate import RpcClient

class ProcessBackup(object):
    logger = logging.getLogger(__name__)
    run_proc = [BackupStatus.SNAPSHOTCREATE.value[0],
                BackupStatus.SNAPSHOTDESTROY.value[0]
            ]

    spin_lock = []


    def __init__(self, lock):
        self.client = RpcClient()
        self.lock = lock

    def worker_run(self, proclist, procruntype, data):
        uuid = data.get('server_uuid')
        usetype = data.get('usetype')
        nodetype = data.get('nodetype')
        name = data.get('name')

        # else:
        #     proclist = self.run_proc

        worker = BackupWorker(run_func=ProcessBackup.backup_proc, uuid=uuid, usetype=usetype, nodetype=nodetype,
                              name=name, proclist=proclist, client=self.client, data=data, procruntype=procruntype,
                              unlock_func=self.lock.unsetlock)
        worker.run()

    def log_kind(self, usetype, nodetype):
        if usetype.upper().__eq__('DATA') and nodetype.upper().__eq__('COMPUTE'):
            proclist = BackupStatus.PROC_INCREMENT_FREEBSD.value
            procruntype = 'data increment'
            proc_run_str = "DATA BACKUP[INCREMENT]"
        elif usetype.upper().__eq__('OS') and nodetype.upper().__eq__('COMPUTE'):
            proclist = BackupStatus.PROC_INCREMENT_FREEBSD.value
            procruntype = 'os increment'
            proc_run_str = "OS BACKUP[INCREMENT]"
        elif usetype.upper().__eq__('OS') and nodetype.upper().__eq__('STORAGE'):
            proclist = BackupStatus.PROC_FULL_FREEBSD.value
            procruntype = "os full[storage]"
            proc_run_str = "STORAGE OS BACKUP[FULL]"
        elif usetype.upper().__eq__('ORIGIN') and nodetype.upper().__eq__('STORAGE'):
            proclist = BackupStatus.PROC_FULL_FREEBSD.value
            procruntype = "os full[storage origin]"
            proc_run_str = "STORAGE OS BACKUP[FULL, ORIGIN]"
        elif usetype.upper().__eq__('DATA') and nodetype.upper().__eq__('MASTER'):
            proclist = BackupStatus.PROC_RSYNC_DATA.value
            procruntype = "data increment[master]"
            proc_run_str = "MASTER DATA BACKUP[INCREMENT]"
        elif usetype.upper().__eq__('OS') and nodetype.upper().__eq__('MASTER'):
            proclist = BackupStatus.PROC_RSYNC_FULL.value
            procruntype = "os full[master]"
            proc_run_str = "MASTER OS BACKUP[FULL]"
        elif usetype.upper().__eq__('ORIGIN') and nodetype.upper().__eq__('MASTER'):
            proclist = BackupStatus.PROC_RSYNC_FULL.value
            procruntype = "os full[master origin]"
            proc_run_str = "MASTER OS BACKUP[FULL, ORIGIN]"

        return proclist, procruntype, proc_run_str

    def run(self, data):
        usetype = data.get('usetype')
        nodetype = data.get('nodetype')

        if self.lock.setlock(data.get('server_uuid')):
            proclist, procruntype, proc_run_str = self.log_kind(usetype, nodetype)
            log_data = {'server_uuid': data.get('server_uuid'), 'target_uuid': data.get('target_uuid'),
                        'nodetype': nodetype, 'usetype': usetype, 'name': data.get('name'),
                        'action_kind': procruntype, 'kind': 'backup',
                        'action_message': proc_run_str, 'action_status': "START"}
            res = self.client.db_send("processhistory", msg=log_data)
            data['run_uuid'] = res.get('run_uuid')
            self.worker_run(proclist, procruntype, data)
            runstatus = "S"
            runprocuuid = res.get('run_uuid')
        else:
            runstatus = "R"
            runprocuuid = None


        return {'runstatus': runstatus, 'runprocuuid': runprocuuid}


    @staticmethod
    def backup_proc(uuid, usetype, nodetype, name, proclist, client, data, procruntype, unlock_func):

        def processhistory(action_kind,
                           message,
                           status,
                           run_uuid = None,
                           errcode = None,
                           errstr = None):
            log_data = { 'server_uuid': data.get('server_uuid'), 'target_uuid': data.get('target_uuid'),
                     'nodetype': nodetype, 'usetype': usetype, 'name': name,
                     'action_kind': action_kind, 'kind': 'backup',
                     'action_message': message, 'action_status': status}
            if run_uuid is not None:
                log_data['run_uuid'] = run_uuid
            if errcode is not None:
                log_data['err_code'] = errcode
            log_data['err_message'] = errstr

            response = client.db_send("processhistory", msg=log_data)
            return response

        action_kind = procruntype
        run_uuid = data.get('run_uuid')
        if procruntype.__eq__('data increment'):
            proc_run_str = "DATA BACKUP[INCREMENT]"
        elif procruntype.__eq__('os increment'):
            proc_run_str = "OS BACKUP[INCREMENT]"
        elif procruntype.__eq__('os full[master]'):
            # data['name'] = "/"
            proc_run_str = "MASTER OS BACKUP[FULL]"
        elif procruntype.__eq__('data increment[master]'):
            # hardcode
            # data['name'] = "/data"
            proc_run_str = "MASTER DATA BACKUP[INCREMENT]"
        elif procruntype.__eq__('os full[master origin]'):
            # data['name'] = "/"
            proc_run_str = "MASTER OS BACKUP[FULL, ORIGIN]"
        elif procruntype.__eq__('data increment[master origin]'):
            # data['name'] = "/"
            proc_run_str = "MASTER DATA BACKUP[INCREMENT, ORIGIN]"
        elif procruntype.__eq__('os full[storage]'):
            #hardcode
            # data['name'] = "master"
            proc_run_str = "STORAGE OS BACKUP[FULL]"
        elif procruntype.__eq__('os full[storage origin]'):
            # hardcode
            # data['name'] = "master"
            proc_run_str = "STORAGE OS BACKUP[FULL, ORIGIN]"

        try:

            # processhistory(action_kind)
            for proc in proclist:
                data['proc'] = proc
                for enum_key in BackupStatus.PROC_ALL_LIST.value:
                    if enum_key[0].__eq__(proc):
                        msg = enum_key[1]
                        break
                ProcessBackup.logger.info("loggmessage : {}".format(msg))
                ProcessBackup.logger.info("BACKUP PROC : {}".format(proc))
                processhistory(action_kind=action_kind, message=msg, status="RUN", run_uuid=run_uuid)
                if BackupStatus.ZVOLMETADATAGET.value[0].__eq__(proc):
                    msg = BackupStatus.ZVOLMETADATAGET.value[1]
                    resp = client.db_send("getlastsnapdata", data)
                    data['dbmetadata'] = resp
                elif BackupStatus.RSYNCGETDATA.value[0].__eq__(proc):
                    resp = client.db_send("getlastsnapdata", data)
                    data['dbmetadata'] = resp
                elif BackupStatus.INCREMENTPOLICE.value[0].__eq__(proc):
                    resp = client.db_send("namekocommtest", {'proc': 'increment police get'})
                    data['police'] = None
                elif BackupStatus.METADATAUPDATE.value[0].__eq__(proc):
                    ProcessBackup.logger.info('save data : {}'.format(data))
                    propertys = data.get('cur_collectdata').get('cur_property')
                    zpool_propertys = []
                    zfs_propertys = []
                    notsave_zfs_property_list = ['creation','used','available','referenced']
                    notsave_zpool_property_list = ['size', 'capacity', 'guid', 'free', 'allocated']
                    ProcessBackup.logger.info("propertys ====> {}".format(propertys))
                    for property in propertys:
                        zfspropertys = property.get('zfs_property')
                        zpoolpropertys = property.get('zpool_property')
                        ProcessBackup.logger.info("zfspropertys ====> {}".format(zfspropertys))
                        ProcessBackup.logger.info("zpoolpropertys ====> {}".format(zpoolpropertys))
                        for zfsproperty_data in zfspropertys:
                            issave = True
                            dataset = zfsproperty_data.get('dataset')
                            zfstype = zfsproperty_data.get('zfstype')
                            zpool = zfsproperty_data.get('zpool')
                            for pro in zfs_propertys:
                                if pro.get('dataset').__eq__(dataset):
                                    issave = False
                            if issave:
                                save_propertys = zfsproperty_data.get('propertys')
                                for savedata in save_propertys:
                                    k = savedata.get('property')
                                    v = savedata.get('value')
                                    s = savedata.get('source')
                                    issaveword = True
                                    for save_word in notsave_zfs_property_list:
                                        if save_word.__eq__(k):
                                            issaveword = False

                                    if issaveword:
                                        save_data = {
                                                'name': data.get('name'),
                                                'dataset':dataset, 'zfstype':zfstype, 'pool':zpool,
                                                'property':k, 'value': v ,'source': s
                                                }
                                        zfs_propertys.append(save_data)

                        for zpoolproperty_data in zpoolpropertys:
                            issave = True
                            dataset = zpoolproperty_data.get('dataset')
                            zfstype = zpoolproperty_data.get('zfstype')
                            zpool = zpoolproperty_data.get('zpool')
                            for pro in zpool_propertys:
                                if pro.get('dataset').__eq__(dataset):
                                    issave = False
                            if issave:
                                save_propertys = zpoolproperty_data.get('propertys')
                                for savedata in save_propertys:
                                    k = savedata.get('property')
                                    v = savedata.get('value')
                                    s = savedata.get('source')
                                    issaveword = True
                                    for save_word in notsave_zpool_property_list:
                                        if save_word.__eq__(k):
                                            issaveword = False
                                    if issaveword:
                                        save_data = {
                                                'dataset': dataset, 'zfstype': zfstype, 'pool': zpool,
                                                'property': k, 'value': v, 'source': s
                                        }
                                        zpool_propertys.append(save_data)

                    boot_pool = data.get('cur_collectdata').get('cur_boot_pool')
                    boot_path = data.get('cur_collectdata').get('cur_boot_path')
                    boot_devname = data.get('cur_collectdata').get('cur_boot_devname')
                    devlist = data.get('cur_collectdata').get('cur_devlist')
                    boot_data = {'pool':boot_pool, 'path':boot_path, 'devname':boot_devname}
                    save_meta = {'poollist': data.get('cur_collectdata').get('cur_poollist'),
                                 'zpool_property': zpool_propertys,
                                 'zfs_property': zfs_propertys,
                                 'uuid': data.get('server_uuid'),
                                 'target_uuid':data.get('target_uuid'),
                                 'nodetype': data.get('nodetype'),
                                 'usetype': data.get('usetype'),
                                 'name': data.get('name'),
                                 'sanpmeta' : data.get('save_snap_meta'),
                                 'bootdata': boot_data,
                                 'devlist':devlist,
                                 'iscsiinfo': data.get('iscsiinfo')}
                    res = client.db_send("savemetadata", save_meta)
                    ProcessBackup.logger.info("\n\nsave meta info : {}\n\n".format(res))
                    if 'issave' in res:
                        issave = res.get('issave')
                        if not issave:
                            ProcessBackup.logger.info("\n\nmeta data save failed\n")
                elif BackupStatus.RSYNCMETADATAUPDATE.value[0].__eq__(proc):
                    save_meta = {'poollist': None,
                                 'zpool_property': None,
                                 'zfs_property': None,
                                 'uuid': data.get('server_uuid'),
                                 'target_uuid': data.get('target_uuid'),
                                 'nodetype': data.get('nodetype'),
                                 'usetype': data.get('usetype'),
                                 'name': data.get('name'),
                                 'sanpmeta': [data.get('snapdata')],
                                 'bootdata': data.get('bootdata'),
                                 'devlist': data.get('devlist')}
                    res = client.db_send("savemetadata", save_meta)
                    ProcessBackup.logger.info("\n\nsave meta info : {}\n\n".format(res))
                else:
                    data = client.backup_send(data.get('modulename'), "backupproc", data)
                    resp = data
                processhistory(action_kind=action_kind, message=msg, status="PASS", run_uuid=run_uuid)
                # ProcessBackup.logger.info("BACKUP COM TEST: {}".format(resp))

            # resp = client.db_send("namekocommtest", {'test': 'backup_proc community test'})
            # ProcessBackup.logger.info("BACKUP PROC COM TEST: {}".format(resp))
            unlock_func(uuid)
            processhistory(action_kind=action_kind, message=proc_run_str, status="END", run_uuid=run_uuid)
        except Exception as e:
            unlock_func(uuid)
            processhistory(action_kind=action_kind, message=msg, status="ERROR", run_uuid=run_uuid,
                           errcode="6020", errstr="RUNTIME ERROR")
            ProcessBackup.logger.info("[proc {}] EXCEPTION {}".format(proc, e))



