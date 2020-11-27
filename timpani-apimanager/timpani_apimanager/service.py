# from .apimanager_pb2 import ActionResponse, ResgisterResponse
# from .apimanager_pb2_grpc import ApimanagerServiceStub
#
# from timpani_framework.grpc.entrypoint import Grpc
# from google.protobuf import json_format
# from .api.dbmanager import dbmanagerClient
# import json
# import dmidecode
#
# grpc = Grpc.implementing(ApimanagerServiceStub)
#
#
# from timpani_dbmanager.dbmanager_pb2 import ActionRequest, ActionResponse
# from timpani_dbmanager.dbmanager_pb2_grpc import DbmanagerServiceStub
# from timpani_framework.grpc.dependency_provider import GrpcProxy
# from timpani_framework.grpc.entrypoint import grpc_client
#
# class ClientService:
#     name = "apimanager_client"
#     client = GrpcProxy("//127.0.0.1", DbmanagerServiceStub)
#
#     @grpc_client
#     def Method(self, action, method, msg_dict):
#         request = ActionRequest(action=1, msgid=1, method="test", msg=json.dumps(msg_dict))
#         responses = self.client.action(request)
#         return responses
#
# # ActionRequest
# # int32 action = 1;
# # int32 msgid = 2;
# # string method = 3;
# # google.protobuf.Struct message = 4;
#
# def get_system_uuid():
#     dmi = dmidecode.DMIDecode()
#     return dmi.get("System")[0].get("UUID")
#
# class ApiManagerService:
#     name = 'apimanager_service'
#
#     # print("Node UUID : {}".format(get_system_uuid()))
#     # run=False
#     # if not run:
#     #     print("Not UUID")
#     #     exit()
#     #
#     dbmanager = dbmanagerClient()
#     client = GrpcProxy("//127.0.0.1", DbmanagerServiceStub)
#
#     def Method(self, action, method, msg_dict):
#         request = ActionRequest(action=1, msgid=1, method="test", msg=json.dumps(msg_dict))
#         responses = self.client.action(request)
#         return responses
#
#
#     @grpc
#     def action(self, request, context):
#         print('request : {}'.format(request))
#         print('action : {}'.format(request.action))
#         print('msgid : {}'.format(request.msgid))
#         print('method : {}'.format(request.method))
#         print('msg : {}'.format(json.loads(request.msg)))
#         call_method = getattr(self.dbmanager,request.method)
#         print("======================")
#         responses = call_method(action=request.action, msg=request.msg, func = self.Method)
#
#         # msg_dict = json.loads(request.msg)
#         # method = "test1"
#         # responses = self.Method(action=request.action, method=method, msg_dict=msg_dict)
#         msg = None
#         if responses is None:
#             msg = "error"
#
#         return ActionResponse(
#             result='success',
#             msgid=request.msgid,
#             method=request.method,
#             msg=msg or responses.msg
#         )




###############################################################################################################33
from nameko.rpc import rpc, RpcProxy

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
# from .api.node import NodeAPI


class ApimanagerService(object):
    name = 'apimanager_service'

    dbmanager_rpc = RpcProxy('dbmanager_service')
    servicemanager_rpc = RpcProxy('service_manager')

    def db_send(self, method, msg):
        call_method = getattr(self.dbmanager_rpc, method)
        response = call_method.call_async(msg)
        return response.result()

    def service_send(self, method, msg, instance):
        call_method = getattr(instance, method)
        response = call_method.call_async(msg)
        return response.result()

    def ipmi_connection_check(self, data):
        is_ipmi_conn = self.service_send('ipmiConnectionCheck', data, self.servicemanager_rpc)
        if is_ipmi_conn.get('is_conn'):
            return True, is_ipmi_conn.get('node_uuid')
        else:
            return False, '-'

    @rpc
    def registerNode(self, data):
        logger.info('RegisterNode {}'.format(data))
        is_discover, node_uuid = self.ipmi_connection_check(data)

        if is_discover:
            data['node_uuid'] = node_uuid
            data['ipmi_info']['is_discovery'] = 1
        else:
            errorcode = "1001"
            errorstr = "IPMI Discovery Failed"
            responses = {'errorcode': errorcode, 'errorstr': errorstr, 'page_msg': data.get('page_msg')}
            return responses

        response = self.db_send(method='registerNode', msg=data)
        logger.info('RegisterNode Response {}'.format(response))
        return response


    # All Node List
    @rpc
    def getNodeList(self, data):
        logger.info("getNodeList {}".format(data))
        response = self.db_send(method='getNodeList', msg=data)
        return response

    # Leader Node List
    @rpc
    def getNodeLeaderList(self, data):
        logger.info("getNodeLeaderList {}".format(data))
        response = self.db_send(method='getNodeLeaderList', msg=data)
        return response


    # Compute Node List
    @rpc
    def getNodeComputeList(self, data):
        logger.info("getNodeComputeList nodeuuid : {}".format(data.get('nodeuuid')))
        response = self.db_send(method='getNodeComputeList', msg=data)
        return response


    # Get Node Info
    @rpc
    def getNodeInfo(self, data):
        logger.info("getNodeInfo nodeuuid : {}".format(data.get('nodeuuid')))
        response = self.db_send(method='getNodeInfo', msg=data)
        return response


    # Updete Node
    @rpc
    def updateNode(self, data):
        logger.info("updateNode: nodeuuid : {}".format(data.get('nodeuuid')))
        response = self.db_send(method='updateNode', msg=data)
        return response

    # Delete Node Info
    @rpc
    def deleteNode(self, data):
        logger.info("deleteNode nodeuuid : {}".format(data.get('nodeuuid')))
        response = self.db_send(method='deleteNode', msg=data)
        return response

    @rpc
    def registerIPMIConn(self, data):
        logger.info("registerIPMIConn: {}".format(data))
        # IPMI COnnection Check
        is_ipmi_conn = 1
        data['is_discovery'] = is_ipmi_conn
        response = self.db_send(method='registerIPMIConn', msg=data)
        return response

    @rpc
    def updateIPMIConn(self, data):
        logger.info("registerIPMIConn: {}".format(data))
        response = self.db_send(method='updateIPMIConn', msg=data)
        return response

    @rpc
    def deleteIPMIConn(self, data):
        logger.info("registerIPMIConn: {}".format(data))
        response = self.db_send(method='deleteIPMIConn', msg=data)
        return response
