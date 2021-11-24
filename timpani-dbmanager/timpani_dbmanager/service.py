import sys
from nameko.rpc import rpc
from .api.node import NodeAPI
from .api.ipmi import IpmiAPI
from .api.system import SystemAPI
from .api.bios import BiosAPI
from .api.user import UserAPI
from .api.sync import SyncAPI
from .api.app import AppAPI
from .api.backupmeta import MetaAPI

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


    # Timpani Config File Save
    app_api = AppAPI()
    config = ConfigrationFileReader()
    config_data, db_config_data = config.read_file()
    DBConnectHandler.initalize_db_connection_handler()
    try:
        app_api.setconfig(db_config_data.get('GENERAL'))
    except Exception as e:
        logger.info("Config File Read Failed : {}".format(e))
        sys.exit()

    node_api = NodeAPI()
    ipmi_api = IpmiAPI()
    system_api = SystemAPI()
    bios_api = BiosAPI()
    user_api = UserAPI()
    sync_api = SyncAPI()
    meta_api = MetaAPI()
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

    #new history
    @rpc
    def getrealhist(self, data):
        return self.system_api.getreallog(data)

    @rpc
    def getprocesshist(self, data):
        return self.system_api.getprocesshistory(data)

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

    @rpc
    def getnodelist(self, data):
        return self.sync_api.getnodelist(data)

    @rpc
    def getvolumelist(self, data):
        return self.sync_api.getvolumelist(data)

    ############################ GET APP CONFIG ##########################
    @rpc
    def getappconfig(self, data):
        return self.app_api.getconfig(data)

    @rpc
    def getnodetype(self, data):
        return self.sync_api.getNodetype(data)

    @rpc
    def addservice(self, data):
        return self.app_api.addservice(data)

    @rpc
    def keepalive(self, data):
        return self.app_api.keepalive(data)

    @rpc
    def appgetmodulename(self, data):
        return self.app_api.getmodulename(data)

    @rpc
    def savemetadata(self, data):
        return self.meta_api.savemetadata(data)

    @rpc
    def getlastsnapdata(self, data):
        return self.meta_api.getlastsnapdata(data)

    @rpc
    def getrestoresnapdata(self, data):
        return self.meta_api.getrestoresnapdata(data)

    @rpc
    def getrestorelist(self, data):
        return self.meta_api.getrestorelist(data)

    @rpc
    def setbiostemplatedata(self, data):
        logger.info("[setbiostemplatedata] \n {}".format(data))
        avail_data = data.get('avail_data')
        match_data = data.get('match_data')
        template_data = data.get('template_data')
        self.bios_api.setbiosavail(avail_data)
        self.bios_api.setbiosmatch(match_data)
        self.bios_api.setbiostemplate(template_data)
        return {'issucces': True}

    @rpc
    def getbiostemplatedata(self, data):
        template_data = self.bios_api.getbiostemplate(data)
        avail_data = self.bios_api.getbiosavail(data)
        match_data = self.bios_api.getbiosmatch(data)
        return {'avail_data':avail_data, 'match_data':match_data, 'template_data':template_data}

    @rpc
    def gettemplatelist(self, data):
        res = self.bios_api.gettemplatelist(data)
        return res

    @rpc
    def restoredataupdate(self, data):
        res = self.meta_api.restoredataupdate(data)
        return res

    @rpc
    def restoreosupdate(self, data):
        res = self.meta_api.restoreosupdate(data)
        return res

    @rpc
    def setipmisensor(self, data):
        res = self.ipmi_api.setipmisensor(data)
        return res

    @rpc
    def setbiosdata(self, data):
        res = self.bios_api.setbiosdata(data)
        return res

    @rpc
    def setdatadir(self, data):
        res = self.app_api.setdatadir(data)
        return res

    @rpc
    def getdatadir(self, data):
        res = self.app_api.getdatadir(data)
        return res

    @rpc
    def getbiosconfig(self, data):
        res = self.bios_api.getbiosconfig(data)
        return res

    @rpc
    def getcurtemplate(self, data):
        res = self.bios_api.getcurtemplate(data)
        return res

    @rpc
    def getsyscfgdumplist(self, data):
        res = self.bios_api.getsyscfgdumplist(data)
        return res

    @rpc
    def getsyscfgdumpdata(self, data):
        res = self.bios_api.getsyscfgdumpdata(data)
        return res

    @rpc
    def delincrementsnaplist(self, data):
        res = self.meta_api.delincrementsnaplist(data)
        return res

    @rpc
    def delonesnap(self, data):
        res = self.meta_api.delonesnap(data)
        return res

    @rpc
    def delsnapdata(self, data):
        res = self.meta_api.delsnapdata(data)
        return res




