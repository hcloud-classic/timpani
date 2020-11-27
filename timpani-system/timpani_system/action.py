import logging
import threading
import uuid
from timpani_system.zfs import ZFS
from timpani_system.resource import ResourceSystem
import datetime
from multiprocessing import Process, Queue

logger = logging.getLogger(__name__)

class Action(object):
    sentinel = -1
    process_list = []
    def __init__(self, master_queue, msg_queue, cmd_queue):
        self.msg_queue = msg_queue
        self.cmd_queue = cmd_queue
        self.master_queue = master_queue
        self.run_id = None
        self.worker_id = None
        self.container = None
        self.thread_loop = False

    def getNowStr(self, node_name:str):
        now = datetime.datetime.now()
        nowDate = now.strftime('%Y%m%d%H%M%S')
        res = node_name + "-" + nowDate
        return nowDate

    def send_message(self, action, p_id, msg):
        data = {'action': action, 'p_id': p_id, 'msg': msg}
        self.msg_queue.put(data)

    def FullBackup_Worker(self, p_id):
        logger.info("FullBackup_Worker")
        logger.info("TEST")

        snapshot_list, dataset_list, snapname_list = ResourceSystem.getSnapShotList()

        # All Snapshot Destory
        for snapname in snapshot_list:
            ResourceSystem.FullDestorySnapshot(snapname)

        # Get Zpool list data
        zpool_list = ResourceSystem.getZpoolList()
        logger.info("zpool list : {}".format(zpool_list))

        now_date = self.getNowStr("test")
        snapname = "F-{}".format(now_date)
        send_list = []
        for pool in zpool_list:
            # Checksum Test File Create
            zfs_list = ResourceSystem.getZfsList(target=pool, recursive=True)
            logger.info("zfs list : {}".format(zfs_list))
            for dataset, mountpoint in zfs_list:
                create_list = ResourceSystem.FullSnapshot(poolname=dataset, snapname=snapname)
            #     checksum_list = ResourceSystem.timpani_checksum(dataset=dataset, mountpoint=mountpoint)
            #     logger.info("checksum_lsit : {}".format(checksum_list))

            # Create Snapshot
            # create_list = ResourceSystem.FullSnapshot(poolname=pool, snapname=snapname)

            for dataset, _ in zfs_list:
                check_snapshot_str = "{}@{}".format(dataset, snapname)
                for snapshot_name in create_list:
                    if snapshot_name.__eq__(check_snapshot_str):
                        send_list.append(snapshot_name)

        logger.info("send list : {}".format(send_list))
        image_data = {}
        self.send_message('START_SEND_BACKUP', p_id, image_data)

        for send_target in send_list:
            remote_path = '/opt/timpani/{}'.format(send_target.replace('/', '_'))
            res = ResourceSystem.FullBackupSend(send_target=send_target, target_host='backup-server', remote_path=remote_path)
            self.send_message('COMPILE_IMAGE_SEND', p_id, {'snapshot': send_target, 'target_path': remote_path})

        self.send_message('END_SEND_BACKUP', p_id, {})
        self.send_message('END', p_id, {})

    def FullBackup_Consumer(self, q, msg_queue):
        logger.info("FullBackup_Consumer")
        while True:
            data = q.get()
            msg_queue.put(data)
            if data is self.sentinel:
                break


    def FullBackup_Start(self):
        logger.info("FullBackup_Start")
        # msg_q = Queue()
        p_id = uuid.uuid4().hex
        p1 = Process(target=self.FullBackup_Worker, args=(p_id,))
        self.process_list.append((p1,'fullbackup', p_id))
        # p2 = Process(target=self.FullBackup_Consumer, args=(msg_q, self.msg_queue))
        p1.start()
        # p2.start()
        # msg_q.close()
        # msg_q.join_thread()
        p1.join()

    def Worker(self):
        logger.info("Worker Start")
        while self.thread_loop:
            cmd = self.cmd_queue.get()
            logger.info(cmd)
            command = cmd.get('cmd')
            if command.__eq__('FullBackup'):
                thread_id = threading.Thread(target=self.FullBackup_Start)
                thread_id.start()
            elif command.__eq__('Quit'):
                break

        logger.info("Worker End")

    def start(self):
        self.thread_loop = True
        self.run_id = threading.Thread(target=self.run, args=(self.msg_queue, self.master_queue))
        self.worker_id = threading.Thread(target=self.Worker, args=(self.msg_queue, self.cmd_queue))

        self.run_id.start()
        self.worker_id.start()

    def run(self):
        self.thread_loop = True
        while self.thread_loop:
            msg = self.msg_queue.get()
            logger.info(msg)
            action = msg.get('action')
            self.master_queue.put(msg)
            if action.__eq__('END'):
                for instance, kind, p_id in self.process_list:
                    if msg.get('p_id').__eq__(p_id):
                        instance.terminate()
                break


    def end(self):
        self.thread_loop = False
        data = {'cmd': 'Quit'}
        self.cmd_queue.put(data)
        # self.msg_queue.close()
        # self.cmd_queue.close()
        # self.run_id.stop()
        # self.worker_id.stop()

    def FullBackup(self, msg):
        logger.info("FullBackup {}".format(msg))
        data = {'cmd': 'FullBackup'}
        self.cmd_queue.put(data)
