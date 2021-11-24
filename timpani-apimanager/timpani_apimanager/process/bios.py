import logging
from .status.bios import BiosProc
from .worker import BiosWorker
from ..trans.translate import RpcClient

class BiosRunner(object):
    logger = logging.getLogger(__name__)
    spin_lock = []

    def __init__(self, lock):
        self.client = RpcClient()
        self.lock = lock

    def template_init(self, servicename):
        res_data = self.client.bios_send(servicename, 'template_init', None)
        return res_data

    def getsensor(self, servicename, data):
        res_data = self.client.bios_send(servicename, 'getsensor', data)
        return res_data

    def worker_run(self, proclist, procruntype, data):
        nodetype = data.get('nodetype')

        # else:
        #     proclist = self.run_proc

        worker = BiosWorker(run_func=BiosRunner.bios_proc, nodetype=nodetype,
                              proclist=proclist, client=self.client, data=data, procruntype=procruntype,
                              unlock_func=self.lock.unsetlock)
        worker.run()


    def run(self, data):
        nodetype = data.get('nodetype')
        runkind = data.get('runkind')

        if runkind.__eq__('dump'):
            proclist = BiosProc.PROC_DUMP.value
            procruntype = "bios dump"
            proc_run_str = "BIOS CONFIG DUMP"
        elif runkind.__eq__('set'):
            template_name = data.get('name')
            proclist = BiosProc.PROC_SET.value
            procruntype = "bios set"
            proc_run_str = "BIOS TEMPLATE SETTING [{}]".format(template_name)


        if self.lock.setlock(data.get('target_uuid')):
            log_data = {'server_uuid': data.get('server_uuid'), 'target_uuid': data.get('target_uuid'),
                        'nodetype': nodetype, 'usetype': None, 'name': None,
                        'action_kind': procruntype, 'kind': 'bios',
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
    def bios_proc(nodetype, proclist, client, data, procruntype, unlock_func):

        def processhistory(action_kind,
                           message,
                           status,
                           run_uuid = None,
                           errcode = None,
                           errstr = None):
            log_data = { 'server_uuid': data.get('server_uuid'), 'target_uuid': data.get('target_uuid'),
                     'nodetype': nodetype, 'usetype': None, 'name': None,
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
        istemplateset = False
        run_uuid = data.get('run_uuid')
        if procruntype.__eq__('bios dump'):
            proc_run_str = "BIOS CONFIG DUMP"
        elif procruntype.__eq__('bios set'):
            proc_run_str = "BIOS TEMPLATE SET [{}]".format(data.get('name'))
            istemplateset = True

        try:
            # processhistory(action_kind)
            for proc in proclist:
                data['proc'] = proc
                for enum_key in BiosProc.PROC_ALL_LIST.value:
                    if enum_key[0].__eq__(proc):
                        msg = enum_key[1]
                        break
                BiosRunner.logger.info("loggmessage : {}".format(msg))
                BiosRunner.logger.info("BACKUP PROC : {}".format(proc))
                processhistory(action_kind=action_kind, message=msg, status="RUN", run_uuid=run_uuid)
                if BiosProc.GETCURBIOSCONFIG.value[0].__eq__(proc):
                    BiosRunner.logger.info("proc : {}".format(proc))
                    gettemplatedata = client.db_send('getbiostemplatedata', data)
                    data['templatedata'] = gettemplatedata
                    if istemplateset:
                        biosconfig = client.db_send('getbiosconfig', data)
                        data['biosconfig'] = biosconfig
                        BiosRunner.logger.info("biosconfig : {}\n".format(data['biosconfig']))
                    BiosRunner.logger.info("templatedata : {}\n".format(data['templatedata']))

                elif BiosProc.UPDATEBIOSDATA.value[0].__eq__(proc):
                    BiosRunner.logger.info("proc : {}".format(proc))
                    client.db_send('setbiosdata', data)
                else:
                    data = client.backup_send(data.get('modulename'), "biosproc", data)
                    resp = data
                processhistory(action_kind=action_kind, message=msg, status="PASS", run_uuid=run_uuid)

            unlock_func(data.get('target_uuid'))
            processhistory(action_kind=action_kind, message=proc_run_str, status="END", run_uuid=run_uuid)
        except Exception as e:
            unlock_func(data.get('target_uuid'))
            processhistory(action_kind=action_kind, message=msg, status="ERROR", run_uuid=run_uuid,
                           errcode="6020", errstr="RUNTIME ERROR")
            BiosRunner.logger.info("[proc {}] EXCEPTION {}".format(proc, e))

