# from .agent_pb2 import ActionResponse, ResgisterResponse
# from .agent_pb2_grpc import AgentServiceStub
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
# class AgentManagerService:
#     name = 'servicemanager_service'
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


import nameko
from nameko.standalone.rpc import ServiceRpcProxy
from nameko.rpc import rpc, RpcProxy
from timpani_servicemanager.models.default_node import DefaultNode
from timpani_servicemanager.configuration.configuration_file_reader import ConfigrationFileReader
from timpani_servicemanager.configuration.config_set import ConfigSetting

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

class Transfer():
    import timpani_servicemanager.constants

    AMQP_URI = timpani_servicemanager.constants.AMQP_CONFIG

    def __init__(self, amqp_uri):
        self.AMQP_URI = amqp_uri

    def send(self, method, instance, service_name, msg):
        logger.info("[SEND] Service Name : {} ".format(service_name))

        with ServiceRpcProxy(service_name, self.AMQP_URI) as rpc:
            call_method = getattr(rpc, method)
            response = call_method.call_async(msg)
            return response.result()


class ServiceManager(object):
    name = 'service_manager'
    dbmanager_rpc = RpcProxy('dbmanager_service')

    import timpani_servicemanager.constants
    config = ConfigrationFileReader()
    config_set = ConfigSetting(config.read_file())
    config_set.setConfig()
    AMQP_URI = timpani_servicemanager.constants.AMQP_CONFIG

    trans = Transfer(AMQP_URI)

    service_table = []

    def register_service_table(self, capability, system_uuid, agent_uuid):
        not_register_service = True
        for service_capability, service_system_uuid, service_agent_uuid, service_instance, service_name in self.service_table:
            if service_capability.__eq__(capability) and service_agent_uuid.__eq__(agent_uuid):
                not_register_service = False
        if not_register_service:
            service_name = "{}_service_{}".format(capability, system_uuid)
            instance = RpcProxy(service_name)
            self.service_table.append((capability, system_uuid, agent_uuid, instance, service_name))
            logger.info("service_table append : {}".format(self.service_table))
        logger.info("service_table : {}".format(self.service_table))

    def find_service_table(self, capability):
        capability_service = []
        for service_capability, service_system_uuid, service_agnet_uuid, service_instance, service_name in self.service_table:
            logger.info("[find_service_table] capability : {} system_uuid : {} agent_uuid : {} instance : {}".format(service_capability, service_system_uuid, service_agnet_uuid, service_instance))
            if service_capability.__eq__(capability):
                capability_service.append((service_instance, service_name))
        logger.info("[find_service_table] capability_service : {}".format(capability_service))
        return capability_service

    def db_send(self, method, msg):
        call_method = getattr(self.dbmanager_rpc, method)
        response = call_method.call_async(msg)
        return response.result()


    # def send(self, method, instance, service_name, msg):
    #     logger.info("[SEND] Service Name : {} ".format(service_name))
    #
    #     with ClusterRpcProxy() as rpc:
    #         remote_instance = getattr(rpc, service_name)
    #         call_method = getattr(remote_instance, method)
    #         response = call_method.call_async(msg)
    #     return response.result()

    def ipmi_send_all(self, method, msg):
        service_all = self.find_service_table(capability='ipmi')
        ret_table = []
        for service_instance, service_name in service_all:
            logger.info("service_instance [{}]".format(service_instance))
            ret = self.trans.send(method=method, instance=service_instance, service_name= service_name, msg=msg)
            ret_table.append(ret)

        return ret_table

    def filemanager_send(self, method, msg):
        service_all = self.find_service_table(capability='filemanager')
        ret_table = []
        for service_instance, service_name in service_all:
            logger.info("service_instance [{}]".format(service_instance))
            ret = self.trans.send(method=method, instance=service_instance, service_name=service_name, msg=msg)
            ret_table.append(ret)

        return ret_table

    @rpc
    def registerService(self, data):
        '''
        data : {'ipv4address': '192.168.221.202', 'capability': 'system', 'ipv4port': None, 'node_uuid': '9F824D5656C1C83B51991D1DDCB8D5C1'}
        :param data:
        :return: {service_uuid:, node_uuid:, system_id}
        '''
        logger.info("registerService : data = {}".format(data))
        # Search Node
        res_data = self.db_send(method="getNodeInfo", msg=data)
        node_not_find = False
        if res_data is None:
            node_not_find = True

        # logger.info("res_data size : {}".format(len(res_data)))
        if node_not_find:
            logger.info("None Register Node")
            node_data = DefaultNode(data.get('node_uuid'))
            logger.info("New Register Node Data : {}".format(node_data.__dict__))
            res_data = self.db_send(method="registerSystemNode", msg=node_data.__dict__)
        #data['node_uuid'] = data.get('nodeuuid')

        res_data = self.db_send(method="registerAgent", msg=data)

        if 'errorcode' in res_data.keys():
            return res_data
        else:
            self.register_service_table(capability=data.get('capability'), system_uuid=data.get('node_uuid'), agent_uuid=res_data.get('agent_id'))
        return res_data

    @rpc
    def registerSystemInfo(self, data):
        res_data = self.filemanager_send(method="check_directory", msg=data)
        logger.info(res_data)
        res_data = self.db_send(method='registerSystemInfo', msg=data)
        return res_data

    @rpc
    def ipmiConnectionCheck(self, data):            # IPMI Leader Node Find
        data['is_simulation'] = True
        result = self.ipmi_send_all(method='ipmiConnectionCheck', msg=data)
        logger.info("ipmiConnectionCheck result : {}".format(result))
        temp_data = []
        res_data = {}
        for check_result in result:
            logger.info("[ipmiConnectionCheck] check_result : {}".format(check_result))
            logger.info("[ipmiConnectionCheck] node_uuid : {}, agent_id : {}, result : {}".format(
                check_result.get('node_uuid'),check_result.get('agent_id'), check_result.get('result')
            ))
            result_dict = check_result.get('result')
            is_append = True
            if result_dict.get('is_conn'):
                for node_uuid, agent_id in temp_data:
                    if node_uuid.__eq__(result_dict.get('node_uuid')):
                        is_append = False
                    else:
                        is_append = True
                if is_append:
                    temp_data.append((result_dict.get('ipmi_node_uuid'), check_result.get('agent_id')))
        if len(temp_data) > 0:
            res_data['is_conn'] = True
            for node_uuid, _ in temp_data:
                node_uuid_last = node_uuid
            res_data['node_uuid'] = node_uuid_last
        else:
            res_data['is_conn'] = False
            res_data['node_uuid'] = ''

        return res_data

    # BIOS CONFIG DATA SETTING
    @rpc
    def registerBiosInfo(self, data):
        logger.info("[service_manager] registerBiosInfo Enter")
        res_data = self.db_send(method='registerBiosInfo', msg=data)
        return res_data




