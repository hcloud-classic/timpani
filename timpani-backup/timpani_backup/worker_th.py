import logging
import copy
import threading

logger = logging.getLogger(__name__)


class Worker(object):

    name = 'work_thread'

    def __init__(self, data, check_func, run_func,
                 node_uuid, remote_path_base, backup_host, amqp_url, snapshot_list,
                 check_max_count=5):
        self.data = copy.deepcopy(data)
        self.check_func = check_func
        self.run_func = run_func
        self.check_max_count = check_max_count
        self.check_cnt = 0
        self.node_uuid = node_uuid
        self.remote_path_base = remote_path_base
        self.backup_host = backup_host
        self.snapshot_list = snapshot_list
        self.amqp_url = amqp_url
        self.run_status = False

    def run_func_start(self):
        thread_id = threading.Thread(target=self.run_func, args=(self.data, self.node_uuid,
                                                                 self.remote_path_base,
                                                                 self.snapshot_list,
                                                                 self.backup_host,
                                                                 self.amqp_url))
        thread_id.start()

    def run(self):
        logger.debug('work thread running ..... ')
        if not self.run_status:
            self.run_func_start()

        res = self.check_func(self.data)
        if 'result' in res:
            if res['result'].__eq__('Y'):
                threading.Timer(3, self.run).start()



