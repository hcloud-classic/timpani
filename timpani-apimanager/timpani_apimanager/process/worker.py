import logging
import copy
import threading

logger = logging.getLogger(__name__)


class BackupWorker(object):

    name = 'work_thread'

    def __init__(self, run_func, uuid, usetype, nodetype, name, proclist, client, data, procruntype, unlock_func):
        self.name = name
        self.run_func = run_func
        self.unlock_func = unlock_func
        self.uuid = uuid
        self.usetype = usetype
        self.nodetype = nodetype
        self.proclist = proclist
        self.client = client
        self.procruntype = procruntype
        self.run_status = False
        self.data = data

    def run_func_start(self):
        thread_id = threading.Thread(target=self.run_func, args=(self.uuid, self.usetype,
                                                                 self.nodetype,
                                                                 self.name,
                                                                 self.proclist,
                                                                 self.client,
                                                                 self.data,
                                                                 self.procruntype,
                                                                 self.unlock_func))
        thread_id.start()

    def run(self):
        logger.debug('work thread running ..... ')
        if not self.run_status:
            self.run_func_start()

        # res = self.check_func(self.data)
        # if 'result' in res:
        #     if res['result'].__eq__('Y'):
        #         threading.Timer(3, self.run).start()

class RestoreWorker(object):

    name = 'work_restore_thread'

    def __init__(self, run_func, usetype, nodetype, name, proclist, client, data, procruntype, unlock_func):
        self.name = name
        self.run_func = run_func
        self.unlock_func = unlock_func
        self.usetype = usetype
        self.nodetype = nodetype
        self.proclist = proclist
        self.client = client
        self.procruntype = procruntype
        self.run_status = False
        self.data = data

    def run_func_start(self):
        thread_id = threading.Thread(target=self.run_func, args=(self.usetype,
                                                                 self.nodetype,
                                                                 self.name,
                                                                 self.proclist,
                                                                 self.client,
                                                                 self.data,
                                                                 self.procruntype,
                                                                 self.unlock_func))
        thread_id.start()

    def run(self):
        logger.debug('work thread running ..... ')
        if not self.run_status:
            self.run_func_start()


class BiosWorker(object):

    name = 'work_bios_thread'

    def __init__(self, run_func, nodetype, proclist, client, data, procruntype, unlock_func):
        self.run_func = run_func
        self.unlock_func = unlock_func
        self.nodetype = nodetype
        self.proclist = proclist
        self.client = client
        self.procruntype = procruntype
        self.run_status = False
        self.data = data

    def run_func_start(self):
        thread_id = threading.Thread(target=self.run_func, args=(self.nodetype,
                                                                 self.proclist,
                                                                 self.client,
                                                                 self.data,
                                                                 self.procruntype,
                                                                 self.unlock_func))
        thread_id.start()

    def run(self):
        logger.debug('work thread running ..... ')
        if not self.run_status:
            self.run_func_start()

class DeleteWorker(object):

    name = 'work_delete_thread'

    def __init__(self, run_func, nodetype, proclist, client, data, procruntype, unlock_func):
        self.run_func = run_func
        self.unlock_func = unlock_func
        self.nodetype = nodetype
        self.proclist = proclist
        self.client = client
        self.procruntype = procruntype
        self.run_status = False
        self.data = data

    def run_func_start(self):
        thread_id = threading.Thread(target=self.run_func, args=(self.nodetype,
                                                                 self.proclist,
                                                                 self.client,
                                                                 self.data,
                                                                 self.procruntype,
                                                                 self.unlock_func))
        thread_id.start()

    def run(self):
        logger.debug('work thread running ..... ')
        if not self.run_status:
            self.run_func_start()
