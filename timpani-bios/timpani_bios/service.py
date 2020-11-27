# import logging
# from .bios_pb2 import ActionResponse, ResgisterResponse
# from .bios_pb2_grpc import BiosServiceStub
#
# from timpani_framework.grpc.entrypoint import Grpc
# from google.protobuf import json_format
# import json
#
# from .syscfg.biosconfig import BiosConfig
# from .trans import dbmanagerClient
#
# import logging.handlers
# logger = logging.getLogger(__name__)
# logger.setLevel(level=logging.DEBUG)
# formatter = logging.Formatter('[%(asctime)s.%(msecs)03d][%(levelname)-8s] %(message)s : (%(filename)s:%(lineno)s)', datefmt="%Y-%m-%d %H:%M:%S")
# fileHandler = logging.handlers.TimedRotatingFileHandler(filename='./log_webmanager.log', when='midnight', backupCount=0, interval=1, encoding='utf-8')
# fileHandler.setFormatter(formatter)
# logger.addHandler(fileHandler)
#
# grpc = Grpc.implementing(BiosServiceStub)
#
#
#
# # ActionRequest
# # int32 action = 1;
# # int32 msgid = 2;
# # string method = 3;
# # google.protobuf.Struct message = 4;
#
# class BiosService:
#     name = 'apimanager_service'
#     print("==================")
#     try:
#         logger.info("[INIT] Send BIOS Configuration Info")
#         bios = BiosConfig()
#         bios_config_info = bios.read_syscfg("test_syscfg.INI")
#         logger.info(bios_config_info)
#         client = dbmanagerClient()
#         response = client.set_syscfg_info(action=1,msg=bios_config_info)
#     except Exception as exec:
#         logger.info("[ERROR] Init Failed : {}".format(str(exec)))
#         exit()
#
#
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
#
# from timpani_dbmanager.dbmanager_pb2 import ActionResponse, ActionRequest
# from timpani_dbmanager.dbmanager_pb2_grpc2 import Db
# class ClientService:
#     name = "apimanager_client"
#
#     grpc_client = GrpcProxy("//127.0.0.1", )

import logging
import timpani_bios.constants
from nameko.rpc import rpc

from timpani_bios.configuration.configuration_file_reader import ConfigrationFileReader
from timpani_bios.configuration.config_set import ConfigSetting
from timpani_bios.configuration.register_service import RegisterService
from timpani_bios.transfer import TransferServiceManager
from .syscfg.biosconfig import BiosConfig


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

# class Threading_Schedule(object):
#     name="threading_schedule"
#
#     def __init__(self, check_func, run_func, check_max_count=5):
#         self.dic_data = copy.deepcopy(dic_data)
#         self.check_func = check_func
#         self.run_func = run_func
#         self.check_max_count = check_max_count
#         self.check_cnt = 0
#
#     def run(self):
#         logger.info('th_waitcheck running ..... ')
#         res = self.check_func(self.dic_data)
#         if 'result' in res:
#             if res['result'].__eq__('Y'):
#                 if self.check_cnt < self.check_max_count:
#                     self.check_cnt += 1
#                     threading.Timer(30,self.run).start()
#                 else:
#                     self.run_func(self.dic_data)


class ServiceInit(object):

    def __init__(self):
        import timpani_bios.constants
        config = ConfigrationFileReader()
        config_set = ConfigSetting(config.read_file())
        config_set.setConfig()
        self.service_manager_trans = TransferServiceManager(timpani_bios.constants.AMQP_CONFIG)
        service_data = RegisterService(node_uuid=timpani_bios.constants.NODE_UUID,
                                   capability=timpani_bios.constants.CAPABILITY,
                                   ipv4address=timpani_bios.constants.SERVICE_IPV4ADDR)

        # get Agent ID
        res_data = self.service_manager_trans.send(method="registerService", service_name='service_manager', msg=service_data.__dict__)
        if 'agent_id' in res_data.keys():
            timpani_bios.constants.AGENT_ID = res_data.get('agent_id')
        else:
            logger.info("GET Agent KEY FAILED")
            exit()

        self.node_uuid = timpani_bios.constants.NODE_UUID
        self.agent_id = timpani_bios.constants.AGENT_ID
        self.default_syscfg_path = timpani_bios.constants.DEFAULT_BIOS_SYSCFG
        self.service_name = "{}_service_{}".format(timpani_bios.constants.CAPABILITY, timpani_bios.constants.NODE_UUID)

    def service_send(self, method, msg):
        ret = self.service_manager_trans.send(method=method, service_name='service_manager', msg=msg)
        return ret

class BiosService(object):
    
    init_data = ServiceInit()
    name = init_data.service_name
    node_uuid = init_data.node_uuid
    agent_id = init_data.agent_id
    syscfg_path = init_data.default_syscfg_path
    service_send = init_data.service_send

    logger.info("name : {}, node_uuid : {}, agent_id : {}".format(__name__, node_uuid, agent_id))

    # Schedule Setting

    # Update Bios Data
    print("[INIT] Send BIOS Configuration Info")
    bios = BiosConfig()
    bios_config_info = bios.read_syscfg(syscfg_path)
    bios_data = {'node_uuid' : node_uuid, 'agent_id' : agent_id, 'bios_config' : bios_config_info}
    # logger.info("syscfg_config : {}".format(bios_config_info))
    service_send(method="registerBiosInfo", msg=bios_data)



    @rpc
    def test(self,data):
        return data