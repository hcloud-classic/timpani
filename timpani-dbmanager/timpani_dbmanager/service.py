# from .dbmanager_pb2 import ActionResponse, ResgisterResponse
# from .dbmanager_pb2_grpc import DbmanagerServiceStub
#
# from timpani_framework.grpc.entrypoint import Grpc
# from google.protobuf import json_format
# import json
#
# grpc = Grpc.implementing(DbmanagerServiceStub)
#
#
# # ActionRequest
# # int32 action = 1;
# # int32 msgid = 2;
# # string method = 3;
# # google.protobuf.Struct message = 4;
#
# class DbManagerService:
#     name = 'dbmanager_service'
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
##################################################################################################

from nameko.rpc import rpc
from .api.node import NodeAPI
from .api.ipmi import IpmiAPI
from .api.system import SystemAPI
from .api.bios import BiosAPI

from timpani_dbmanager.db.db_connect_handler import DBConnectHandler
from timpani_dbmanager.configuration.configuration_file_reader import ConfigrationFileReader

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

class DbmanagerService(object):
    name = 'dbmanager_service'

    ConfigrationFileReader()
    DBConnectHandler.initalize_db_connection_handler()

    node_api = NodeAPI()
    ipmi_api = IpmiAPI()
    system_api = SystemAPI()
    bios_api = BiosAPI()

    print("RUN {}".format(name))

    @rpc
    def registerNode(self, data):
        return self.node_api.registerNode(data)

    @rpc
    def registerSystemNode(self, data):
        return self.node_api.registerSystemNode(data)

    # All Node List
    @rpc
    def getNodeList(self, data):
        return self.node_api.getNodeList(data)

    # Leader Node List
    @rpc
    def getNodeLeaderList(self, data):
        return self.node_api.getNodeLeaderList(data)

    # Compute Node List
    @rpc
    def getNodeComputeList(self, data):
        return self.node_api.getNodeComputeList(data)

    # Get Node Info
    @rpc
    def getNodeInfo(self, data):
        return self.node_api.getNodeInfo(data)

    # Updete Node
    @rpc
    def updateNode(self, data):
        return self.node_api.updateNode(data)

    # Delete Node Info
    @rpc
    def deleteNode(self, data):
        return self.node_api.deleteNode(data)

    ################### IPMI #############################
    @rpc
    def registerIPMIConn(self, data):
        return self.ipmi_api.registerIPMIConn(data)

    @rpc
    def updateIPMIConn(self, data):
        return self.ipmi_api.updateIPMIConn(data)

    @rpc
    def deleteIPMIConn(self, data):
        return self.ipmi_api.deleteIPMIConn(data)

    #####################################################

    @rpc
    def registerBiosInfo(self, data):
        return self.bios_api.registerBiosInfo(data)

    ######################### System ########################
    @rpc
    def registerAgent(self, data):
        return self.system_api.registerAgent(data)

    ######################### System ########################
    @rpc
    def registerSystemInfo(self, data):
        return self.system_api.registerSystemInfo(data)

    @rpc
    def zfsListData(self, data):
        return 