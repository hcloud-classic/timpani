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
# import timpani_ipmi.constants
from nameko.rpc import rpc

from timpani_ipmi.configuration.configuration_file_reader import ConfigrationFileReader
from timpani_ipmi.configuration.config_set import ConfigSetting
from timpani_ipmi.configuration.register_service import RegisterService
from timpani_ipmi.transfer import TransferServiceManager
from timpani_ipmi.ipmi import IPMIManager


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
        import timpani_ipmi.constants
        config = ConfigrationFileReader()
        config_set = ConfigSetting(config.read_file())
        config_set.setConfig()
        service_manager_trans = TransferServiceManager(timpani_ipmi.constants.AMQP_CONFIG)
        service_data = RegisterService(node_uuid=timpani_ipmi.constants.NODE_UUID,
                                   capability=timpani_ipmi.constants.CAPABILITY,
                                   ipv4address=timpani_ipmi.constants.SERVICE_IPV4ADDR)

        # get Agent ID
        res_data = service_manager_trans.send(method="registerService", service_name='service_manager' ,msg=service_data.__dict__)
        if 'agent_id' in res_data.keys():
            timpani_ipmi.constants.AGENT_ID = res_data.get('agent_id')
        else:
            logger.info("GET Agent KEY FAILED")
            exit()

        self.node_uuid = timpani_ipmi.constants.NODE_UUID
        self.agent_id = timpani_ipmi.constants.AGENT_ID
        self.service_name = "{}_service_{}".format(timpani_ipmi.constants.CAPABILITY, timpani_ipmi.constants.NODE_UUID)


class IpmiService(object):
    init_data = ServiceInit()
    name = init_data.service_name
    node_uuid = init_data.node_uuid
    agent_id = init_data.agent_id
    logger.info("name : {}, node_uuid : {}, agent_id : {}".format(__name__, node_uuid, agent_id))

    # {'node_uuid': _ , 'agent_id' : _, 'result' : {}}
    def return_success(self, result):
        return {'node_uuid' : self.node_uuid, 'agent_id' : self.agent_id, 'result' : result}

    # IPMI Connection Test
    @rpc
    def ipmiConnectionCheck(self, data):
        simulation = data.get('is_simulation')
        is_conn = True
        logger.info("[IPMI][ipmiConnectionCheck] data : {}".format(data))
        if simulation:          # Local Test Debug Option
            type = data.get('node_type')
            tmp_uuid = data.get('node_uuid')
            ip_address = data.get('ipmi_info').get('ipv4addr')
            if ip_address.__eq__('9.9.9.6'): #master
                ipmi_node = "9F824D56-56C1-C83B-5199-1D1DDCB8D5C1"
            elif ip_address.__eq__('9.9.9.7'):
                ipmi_node = "cf754d56-dff2-913a-ce19-36a08cdaa715"
            elif ip_address.__eq__('9.9.9.8'):
                ipmi_node = "cf754d56-dff1-003a-ce19-36a09adaa765"
            elif ip_address.__eq__('9.9.9.9'):
                ipmi_node = "ad755d56-eff1-003a-b1e9-36a19aeaf468"

            if tmp_uuid is None:
                ipmi_node_uuid = self.node_uuid
                is_conn = True
            else:
                if tmp_uuid.__eq__(ipmi_node):
                    ipmi_node_uuid = ipmi_node
                    is_conn = True
                else:
                    ipmi_node_uuid = None
                    is_conn = False
        else:
            try:
                ipmi_node_uuid = IPMIManager.get_ipmi_system_uuid(addr=data.get('ipv4addr'), user=data.get('user'), password=data.get('password'))
                if ipmi_node_uuid is None:
                    is_conn = False
            except:
                ipmi_node_uuid = None
                is_conn = False
        result = {'is_conn' : is_conn, 'ipmi_node_uuid' : ipmi_node_uuid}
        return self.return_success(result)



