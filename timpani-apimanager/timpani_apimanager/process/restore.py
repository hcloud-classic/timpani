import logging
from .status.restore import RestoreStatus
from .worker import RestoreWorker
from ..trans.translate import RpcClient

class ProcessRestore(object):
    logger = logging.getLogger(__name__)
    # run_proc = [BackupStatus.SNAPSHOTCREATE.value[0],
    #             BackupStatus.SNAPSHOTDESTROY.value[0]
    #         ]

    spin_lock = []


    def __init__(self, lock):
        self.client = RpcClient()
        self.lock = lock

    def worker_run(self, proclist, procruntype, data):
        uuid = data.get('server_uuid')
        usetype = data.get('usetype')
        nodetype = data.get('nodetype')
        name = data.get('name')

        worker = RestoreWorker(run_func=ProcessRestore.restore_proc, usetype=usetype, nodetype=nodetype,
                               name=name, proclist=proclist, client=self.client, data=data, procruntype=procruntype,
                               unlock_func=self.lock.unsetlock)
        worker.run()


    def log_kind(self, usetype, nodetype):
        if usetype.upper().__eq__('DATA') and nodetype.upper().__eq__('COMPUTE'):
            proclist = RestoreStatus.PROC_INCREMENT_FREEBSD.value
            procruntype = 'data restore'
            proc_run_str = "DATA RESTORE[INCREMENT]"
        elif usetype.upper().__eq__('OS') and nodetype.upper().__eq__('COMPUTE'):
            proclist = RestoreStatus.PROC_INCREMENT_FREEBSD.value
            procruntype = 'os restore'
            proc_run_str = "OS RESTORE[INCREMENT]"
        elif usetype.upper().__eq__('OS') and nodetype.upper().__eq__('STORAGE'):
            proclist = RestoreStatus.PROC_FULL_FREEBSD.value
            procruntype = "os restore[storage]"
            proc_run_str = "STORAGE OS RESTORE[FULL]"
        elif usetype.upper().__eq__('ORIGIN') and nodetype.upper().__eq__('STORAGE'):
            proclist = RestoreStatus.PROC_FULL_FREEBSD.value
            procruntype = "os restore[storage origin]"
            proc_run_str = "STORAGE OS RESTORE[FULL, ORIGIN]"
        elif usetype.upper().__eq__('DATA') and nodetype.upper().__eq__('MASTER'):
            proclist = RestoreStatus.PROC_RSYNC_DATA.value
            procruntype = "data restore[master]"
            proc_run_str = "MASTER DATA RESTORE[INCREMENT]"
        elif usetype.upper().__eq__('OS') and nodetype.upper().__eq__('MASTER'):
            proclist = RestoreStatus.PROC_RSYNC_OS.value
            procruntype = "os restore[master]"
            proc_run_str = "MASTER OS RESTORE[FULL]"
        elif usetype.upper().__eq__('ORIGIN') and nodetype.upper().__eq__('MASTER'):
            proclist = RestoreStatus.PROC_RSYNC_OS.value
            procruntype = "os restore[master origin]"
            proc_run_str = "MASTER OS RESTORE[FULL, ORIGIN]"

        return proclist, procruntype, proc_run_str

    def run(self, data):
        self.logger.info("RUN : DATA : {}".format(data))
        usetype = data.get('usetype')
        nodetype = data.get('nodetype')
        if self.lock.setlock(data.get('server_uuid')):
            proclist, procruntype, proc_run_str = self.log_kind(usetype, nodetype)
            log_data = {'server_uuid': data.get('server_uuid'), 'target_uuid': data.get('target_uuid'),
                        'nodetype': nodetype, 'usetype': usetype, 'name': data.get('name'),
                        'action_kind': procruntype, 'kind': 'restore',
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
    def restore_proc(usetype, nodetype, name, proclist, client, data, procruntype, unlock_func):

        def processhistory(action_kind,
                           message,
                           status,
                           run_uuid = None,
                           errcode = None,
                           errstr = None):
            log_data = { 'server_uuid': data.get('server_uuid'), 'target_uuid': data.get('target_uuid'),
                     'nodetype': nodetype, 'usetype': usetype, 'name': name,
                     'action_kind': action_kind, 'kind': 'restore',
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
        if procruntype.__eq__('data restore'):
            proc_run_str = "DATA RESTORE[INCREMENT]"
        elif procruntype.__eq__('os restore'):
            proc_run_str = "OS RESTORE[INCREMENT]"
        elif procruntype.__eq__('os restore[master]'):
            proc_run_str = "MASTER OS RESTORE[FULL]"
        elif procruntype.__eq__('data restore[master]'):
            proc_run_str = "MASTER DATA RESTORE[INCREMENT]"
        elif procruntype.__eq__('os restore[master origin]'):
            proc_run_str = "MASTER OS restore[FULL, ORIGIN]"
        elif procruntype.__eq__('data restore[master origin]'):
            proc_run_str = "MASTER DATA RESTORE[INCREMENT, ORIGIN]"
        elif procruntype.__eq__('os restore[storage]'):
            proc_run_str = "STORAGE OS RESTORE[FULL]"
        elif procruntype.__eq__('os restore[storage origin]'):
            proc_run_str = "STORAGE OS RESTORE[FULL, ORIGIN]"

        lock_uuid = data.get('server_uuid')
        try:
            for proc in proclist:
                data['proc'] = proc
                for enum_key in RestoreStatus.PROC_ALL_LIST.value:
                    if enum_key[0].__eq__(proc):
                        msg = enum_key[1]
                        break
                ProcessRestore.logger.info("loggmessage : {}".format(msg))
                ProcessRestore.logger.info("RESTORE PROC : {}".format(proc))
                processhistory(action_kind=action_kind, message=msg, status="RUN", run_uuid=run_uuid)
                if RestoreStatus.ZVOLMETADATAGET.value[0].__eq__(proc):
                    resp = client.db_send("getlastsnapdata", data)
                    data['dbmetadata'] = resp
                elif RestoreStatus.RSYNCPRIVDATACOLLECT.value[0].__eq__(proc):
                    resp = client.db_send("getlastsnapdata", data)
                    data['dbmetadata'] = resp
                elif RestoreStatus.METADATAUPDATE.value[0].__eq__(proc):
                    resp = client.db_send("restoredataupdate", data)
                elif RestoreStatus.METADATAUPDATE_OS.value[0].__eq__(proc):
                    resp = client.db_send("restoreosupdate", data)
                else:
                    data = client.restore_send(data.get('modulename'), "restoreproc", data)
                    resp = data

                processhistory(action_kind=action_kind, message=msg, status="PASS", run_uuid=run_uuid)
                # ProcessRestore.logger.info("Restore COM TEST: {}".format(resp))

            # resp = client.db_send("namekocommtest", {'test': 'backup_proc community test'})
            # ProcessRestore.logger.info("BACKUP PROC COM TEST: {}".format(resp))
            unlock_func(lock_uuid)
            processhistory(action_kind=action_kind, message=proc_run_str, status="END", run_uuid=run_uuid)
        except Exception as e:
            unlock_func(lock_uuid)
            processhistory(action_kind=action_kind, message=msg, status="ERROR", run_uuid=run_uuid,
                           errcode="6020", errstr="RUNTIME ERROR")
            ProcessRestore.logger.info("[proc {}] EXCEPTION {}".format(proc, e))

