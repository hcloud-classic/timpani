import logging
from .status.delete import DeleteProc
from .worker import DeleteWorker
from ..trans.translate import RpcClient

class SnapDelete(object):
    logger = logging.getLogger(__name__)
    spin_lock = []

    def __init__(self, lock):
        self.client = RpcClient()
        self.lock = lock

    def worker_run(self, proclist, procruntype, data):
        nodetype = data.get('nodetype')

        worker = DeleteWorker(run_func=SnapDelete.delete_proc, nodetype=nodetype,
                              proclist=proclist, client=self.client, data=data, procruntype=procruntype,
                              unlock_func=self.lock.unsetlock)
        worker.run()

    def run(self, data):
        nodetype = data.get('nodetype')
        usetype = data.get('usetype')
        name = data.get('snapname')
        runkind = data.get('runkind')

        if runkind.__eq__('snap'):
            proclist = DeleteProc.PROC_SNAP.value
            procruntype = "snapfile delete"
            proc_run_str = "SNAPFILE DELETE"

        if self.lock.setlock(data.get('server_uuid')):
            log_data = {'server_uuid': data.get('server_uuid'), 'target_uuid': data.get('target_uuid'),
                        'nodetype': nodetype, 'usetype': usetype, 'name': name,
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
    def delete_proc(nodetype, proclist, client, data, procruntype, unlock_func):

        def processhistory(action_kind,
                           message,
                           status,
                           run_uuid = None,
                           errcode = None,
                           errstr = None):
            log_data = {'server_uuid': data.get('server_uuid'), 'target_uuid': data.get('target_uuid'),
                        'nodetype': nodetype, 'usetype': data.get('usetype'), 'name': data.get('snapname'),
                        'action_kind': action_kind, 'kind': 'bios',
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
        snapname = data.get('snapname')
        if procruntype.__eq__('snapfile delete'):
            proc_run_str = "{} SNAP FILE DELETE".format(snapname)

        try:
            # processhistory(action_kind)
            for proc in proclist:
                data['proc'] = proc
                for enum_key in DeleteProc.PROC_ALL_LIST.value:
                    if enum_key[0].__eq__(proc):
                        msg_data = enum_key[1]
                        msg = snapname + " " + msg_data
                        break
                SnapDelete.logger.info("loggmessage : {}".format(msg))
                SnapDelete.logger.info("BACKUP PROC : {}".format(proc))
                processhistory(action_kind=action_kind, message=msg, status="RUN", run_uuid=run_uuid)
                if DeleteProc.UPDATEDELETEDATA.value[0].__eq__(proc):
                    SnapDelete.logger.info("UPDATEDELETEDATA :\n {}".format(data))
                    data = client.db_send("delsnapdata", msg=data)
                    SnapDelete.logger.info("DB Delete List : {}".format(data.get('dbdellist')))
                else:
                    data = client.backup_send(data.get('modulename'), "deleteproc", data)
                    resp = data
                processhistory(action_kind=action_kind, message=msg, status="PASS", run_uuid=run_uuid)

            unlock_func(data.get('server_uuid'))
            processhistory(action_kind=action_kind, message=proc_run_str, status="END", run_uuid=run_uuid)
        except Exception as e:
            unlock_func(data.get('server_uuid'))
            processhistory(action_kind=action_kind, message=msg, status="ERROR", run_uuid=run_uuid,
                            errcode="6020", errstr="RUNTIME ERROR")
            SnapDelete.logger.info("[proc {}] EXCEPTION {}".format(proc, e))

