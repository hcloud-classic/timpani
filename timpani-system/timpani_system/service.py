# from .apimanager_pb2 import ActionResponse, ResgisterResponse
# from .apimanager_pb2_grpc import ApimangerServiceStub
#
# from timpani_framework.grpc.entrypoint import Grpc
# from google.protobuf import json_format
# import json
#
# grpc = Grpc.implementing(ApimangerServiceStub)
#
#
# # ActionRequest
# # int32 action = 1;
# # int32 msgid = 2;
# # string method = 3;
# # google.protobuf.Struct message = 4;
#
# class ApiManagerService:
#     name = 'apimanager_service'
#
#     @grpc
#     def action(self, request, context):
#         print('request : {}'.format(request))
#         print('action : {}'.format(request.action))
#         print('msgid : {}'.format(request.msgid))
#         print('method : {}'.format(request.method))
#         print('msg : {}'.format(json.loads(request.msg)))
#         return ActionResponse(
#             result='success',
#             msgid=request.msgid,
#             method=request.method,
#             msg=request.msg
#         )

import logging
import os
import psutil
import threading
import time
import timpani_system.constants
from nameko.rpc import rpc

from timpani_system.configuration.configuration_file_reader import ConfigrationFileReader
from timpani_system.configuration.config_set import ConfigSetting
from timpani_system.configuration.register_service import RegisterService
from timpani_system.transfer import TransferServiceManager
from timpani_system.resource import ResourceSystem
from multiprocessing import Queue
from timpani_system.action import Action
from nameko.extensions import Entrypoint
from functools import partial

import logging.handlers
################################### logger ############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d][%(levelname)-8s] %(message)s : (%(filename)s:%(lineno)s)', datefmt="%Y-%m-%d %H:%M:%S")
fileHandler = logging.handlers.TimedRotatingFileHandler(filename='./log_'+__name__.__str__(), when='midnight', backupCount=0, interval=1, encoding='utf-8')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
stream_hander = logging.StreamHandler()
logger.addHandler(stream_hander)
#######################################################################################################################

class ServiceInit(object):

    def __init__(self):
        import timpani_system.constants
        config = ConfigrationFileReader()
        config_set = ConfigSetting(config.read_file())
        config_set.setConfig()
        self.service_manager_trans = TransferServiceManager(timpani_system.constants.AMQP_CONFIG)
        service_data = RegisterService(node_uuid=timpani_system.constants.NODE_UUID,
                                   capability=timpani_system.constants.CAPABILITY,
                                   ipv4address=timpani_system.constants.SERVICE_IPV4ADDR)

        # get Agent ID
        res_data = self.service_manager_trans.send(method="registerService", service_name='service_manager' ,msg=service_data.__dict__)
        if 'agent_id' in res_data.keys():
            timpani_system.constants.AGENT_ID = res_data.get('agent_id')
        else:
            logger.info("GET Agent KEY FAILED")
            exit()

        self.node_uuid = timpani_system.constants.NODE_UUID
        self.agent_id = timpani_system.constants.AGENT_ID
        self.address = timpani_system.constants.SERVICE_IPV4ADDR
        self.service_name = "{}_service_{}".format(timpani_system.constants.CAPABILITY, timpani_system.constants.NODE_UUID)

    def service_send(self, method, msg):
        ret = self.service_manager_trans.send(method=method, service_name='service_manager', msg=msg)
        return ret

class AsyncAction(Entrypoint):

    def __init__(self, pid, queue, **kwargs):
        self.message_queue = Queue()
        self.cmd_queue = Queue()
        self.master_queue = queue
        self.thread_loop = False
        self.check_id = None
        self.action_id = None
        self.check_pid = pid
        self.action = None
        super(AsyncAction, self).__init__(**kwargs)


    def start(self):
        logger.info("Async_Action Start")
        self.thread_loop = True
        self.action = Action(self.master_queue, self.message_queue, self.cmd_queue)
        # self.action = Action(self.master_queue, self.container)
        # self.action.start()
        # self.container.spawn_managed_thread(self.action.run, identifier="AsyncAction.action.run")

        # self.container.spawn_managed_thread(self.check_process, identifier="AsyncAction.check_process")
        self.container.spawn_managed_thread(self.run, identifier="AsyncAction.run")
        # self.container.spawn_managed_thread(self.Worker, identifier="AsyncAction.Worker")
        # self.container.spawn_managed_thread(self.message_listen, identifier="AsyncAction.check_process")

        # time.sleep(10)
        # self.action_id = threading.Thread(target=self.run)
        # logger.info("action_id : {}".format(self.action_id))
        # self.check_id = threading.Thread(target=self.check_process)
        # self.action_id.start()
        # self.check_id.start()
        logger.info("Async_Action Start [END]")


    def check_process(self):
        logger.info("Async_Action check_process")
        self.thread_loop = True
        while self.thread_loop:
            p = psutil.Process(self.check_pid)
            status = p.status()
            # logger.info("ps status : {}".format(status))
            if (status == psutil.STATUS_ZOMBIE) or (status == psutil.STATUS_DEAD) or (status == psutil.STATUS_STOPPED):
                data = {'action': 'Exit'}
                self.master_queue.put(data)
                break

            time.sleep(1)
        logger.info("Async_Action check_process [END]")

    def Worker(self):
        logger.info("Worker Start")
        self.thread_loop = True
        while self.thread_loop:
            cmd = self.cmd_queue.get()
            logger.info("[Worker] cmd : {}".format(cmd))
            command = cmd.get('cmd')
            if command.__eq__('FullBackup'):
                self.action.FullBackup_Start()
                # thread_id = threading.Thread(target=self.FullBackup_Start)
                # thread_id.start()
            elif command.__eq__('Quit'):
                break

        logger.info("Worker End")

    def message_listen(self):
        self.thread_loop = True
        logger.info("message_listen Start")
        while self.thread_loop:
            msg = self.msg_queue.get()
            logger.info(msg)
            action = msg.get('action')
            self.master_queue.put(msg)


    def run(self):
        # logger.info("Async_Action run")
        self.thread_loop = True
        while self.thread_loop:
            # logger.info("Async_Action run 1")
            msg = self.master_queue.get()
            logger.info("Master Queue : {}".format(msg))
            if msg.get('action').__eq__('Exit'):
                self.action.end()
                self.thread_loop = False
                break
            elif msg.get('action').__eq__('RUN'):
                self.run_method(msg)
            else:
                self.handle_message(msg)

        logger.info("Async_Action run [END]")

    def run_method(self, message):
        logger.info("Async_Action run_method")
        handle_result = partial(self.handle_result, message)
        args = (message,)
        kwargs = {}
        self.container.spawn_worker(
            self, args, kwargs, handle_result=handle_result
        )
        # method = message['method']
        # args = message['args']
        # f = getattr(self.action, method)
        # result = f(args)
        # logger.info("Async_Action run_method [END]")

    def handle_message(self, message):
        logger.info("Async_Action run_message")
        handle_result = partial(self.handle_result, message)
        args = (message,)
        kwargs = {}
        self.container.spawn_worker(
            self, args, kwargs, handle_result=handle_result
        )

    def handle_result(self, message, worker_ctx, result, exc_info):
        if message['action'].__eq__('RUN'):
            logger.info("Async_Action handle_result 1")
            self.action.start()
            logger.info("Async_Action handle_result 2")
            method = message['method']
            args = message['args']
            f = getattr(self.action, method)
            f(args)
        else:
            result=message
        # self.action.FullBackup(message)
        # result = message
        return result, exc_info

    # def handle_message_result(self, message, worker_ctx, result, exc_info):
    #     result = message
    #     return result, exc_info

action_service = AsyncAction.decorator



class SystemService(object):
    init_data = ServiceInit()
    name = init_data.service_name
    node_uuid = init_data.node_uuid
    agent_id = init_data.agent_id
    ip_address = init_data.address
    send_service = init_data.service_send
    logger.info("name : {}, node_uuid : {}, agent_id : {}".format(__name__, node_uuid, agent_id))

    # Register System base information
    # base_info = ResourceSystem.getBaseSystemInfo()
    base_info = ResourceSystem.getBaseInformation()
    base_info['ipv4address'] = timpani_system.constants.SERVICE_IPV4ADDR
    base_info['node_uuid'] = node_uuid
    logger.info("Base System Info : {}".format(base_info))
    system_id = send_service(method="registerSystemInfo", msg=base_info)
    logger.info("Sytem ID : {}".format(system_id))

    pid = os.getpid()
    send_queue = Queue()

    # action_service = AsyncAction(pid)


    @action_service(pid, send_queue)
    def handler_message(self, msg):
        logger.info("handler_message : {}".format(msg))


    @rpc
    def test(self,data):

        return data

    test_data = {'action': 'MSG', 'method': 'FullBackup', 'args': {'test': '123'}}
    send_queue.put(test_data)
    test_data = {'action': 'RUN', 'method': 'FullBackup', 'args': {'test': '123'}}
    send_queue.put(test_data)

