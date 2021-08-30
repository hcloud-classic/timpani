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
from .api.user import UserAPI
from .api.sync import SyncAPI

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
    user_api = UserAPI()
    sync_api = SyncAPI()

    print("RUN {}".format(name))

    @rpc
    def namekocommtest(self, data):
        return data

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

    @rpc
    def SetBackupSrcList(self, data):
        return self.system_api.SetBackupSrc(data)

    @rpc
    def GetBackupSrcList(self, data):
        return self.system_api.GetBackupSrc(data)

    @rpc
    def GetRecoverList(self, data):
        return self.system_api.GetRecoverSrc(data)

    @rpc
    def GetSystemHistory(self, data):
        return self.system_api.GetSystemHistory(data)

    @rpc
    def GetSystemProcessHistory(self, data):
        return self.system_api.GetSystemProcessHistory(data)

    ######################### System ########################
    @rpc
    def registerSystemInfo(self, data):
        return self.system_api.registerSystemInfo(data)

    @rpc
    def zfsListData(self, data):
        return

    @rpc
    def backupmetadata(self, data):
        res_data = self.system_api.backupmetadata(data)
        return data

    @rpc
    def backupmetadata_linux(self, data):
        res_data = self.system_api.backupmetadata_linux(data)
        return data

    @rpc
    def snapshotlist(self, data):
        res_data = self.system_api.snapshotlist(data)
        return data

    # Get SnapshotList
    @rpc
    def GetSnapshotList(self, data):
        logger.debug('GetSnapshotList {}'.format(data))
        res_data = self.system_api.get_snapshotlist(data)
        return res_data

    @rpc
    def GetSnapImageList(self, data):
        logger.debug('GetSnapImageList {}'.format(data))
        res_data = self.system_api.get_snapshotImageList(data)
        return res_data

    @rpc
    def GetTargetImageList(self, data):
        logger.debug('GetSnapImageList {}'.format(data))
        res_data = self.system_api.get_TargetImageList(data)
        return res_data

    @rpc
    def GetIPMIInfo(self, data):
        logger.debug('GetIPMIInfo {}'.format(data))
        res_data = self.ipmi_api.GetIPMIInfo(data)
        return res_data

    @rpc
    def GetRsyncData(self, data):
        logger.debug('GetRsyncData {}'.format(data))
        res_data = self.system_api.get_RsyncBaseData(data)
        return res_data

    @rpc
    def processhistory(self, data):
        res_data = self.system_api.processhistory(data)
        return res_data

    @rpc
    def checkprocessstatus(self, data):
        res_data = self.system_api.checkprocessstatus(data)
        return res_data

    @rpc
    def GetSystemInfo(self, data):
        res_data = self.system_api.getsysteminfo(data)
        return res_data

    ########################### RECOVER ###################
    @rpc
    def getnodeuuid_image(self, data):
        res_data = self.system_api.getnodeuuid_image(data)
        return res_data


    ########################## USER MANAGER NODE LIST ####################
    # return : {'user_id': <String>, 'insert_ok_cnt': <INT>, 'node_uuid_ok_list': [<String>,...,<String>]}
    @rpc
    def registerManagerNodeList(self, data):
        res_data = self.user_api.registerUserManagerNodeList(data)
        return res_data

    # return : {'user_id': <String>, 'node_cnt': <INT> ,'node_list': [<String>,...,<String>]}
    @rpc
    def getManagerNodeList(self, data):
        res_data = self.user_api.getUserManagerNodeList(data)
        return res_data

    ########################### MASTER ACCOUNT ###########################
    @rpc
    def masteradd(self, data):
        # data : {'user_id':<String>,'user_password':<String>}
        # "id_name", "role", "password"
        masterData = {}
        masterData['role'] = 'master'
        masterData['id_name'] = data.get('user_id')
        masterData['password'] = data.get('user_password')
        res_data = self.user_api.masteradd(masterData)

        if 'errorcode' in res_data:
            return False
        else:
            return True

    @rpc
    def masterdel(self, data):
        masterData = {}
        masterData['id_name'] = data.get('user_id')
        res_data = self.user_api.masterdel(masterData)

        if 'errorcode' in res_data:
            return False
        else:
            return True


    ############################# SYNC CHECK ##############################
    @rpc
    def synccheck(self, data):
        return self.sync_api.synccheck(data)

    @rpc
    def mastersync(self, data):
        return self.user_api.masteradd(data)

    @rpc
    def masterinfo(self, data):
        return self.user_api.getmasterinfo(data)




