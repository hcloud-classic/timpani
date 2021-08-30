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
from .process.backup import ProcessBackup

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
    filemanager_rpc = RpcProxy('filemanager_service')
    backup_server_rpc = RpcProxy('backup_server_service')
    proc_backup = ProcessBackup()

    def db_send(self, method, msg):
        call_method = getattr(self.dbmanager_rpc, method)
        response = call_method.call_async(msg)
        return response.result()

    def service_send(self, method: object, msg: object, instance: object) -> object:
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
        if 'node_uuid' in data:
            is_discover = True
            node_uuid = data.get('node_uuid')
        else:
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

    # Show list from Backup target source
    @rpc
    def getbackupsrclist(self, data):
        logger.info("getbackupsrclist: {}".format(data))
        response = self.db_send(method='GetBackupSrcList', msg=data)
        return response

    @rpc
    def getrecoverlist(self, data):
        logger.info("getrecoverlist: {}".format(data))
        response = self.db_send(method='GetRecoverList', msg=data)
        return response

    def rsync_full(self, node_uuid, rsync_base_data, system_info, ipmi_info):
        res_data = {
            'node_uuid' : node_uuid,
            'backup_date' : rsync_base_data.get('backup_date'),
            'home_path' : rsync_base_data.get('home_path'),
            'os' : system_info.get('os_name').lower(),
            'ipmi_info' : ipmi_info
        }
        return res_data

    def zfs_full(self, node_uuid, snap_name, home_path, system_info, ipmi_info):
        res_data = {
            'node_uuid' : node_uuid,
            'snap_name' : snap_name,
            'home_path' : home_path,
            'os' : system_info.get('os_name').lower(),
            'ipmi_info' : ipmi_info
        }
        return res_data

    def rsync_increment(self, data, rsync_base_data, system_info, ipmi_info):
        res_data = {
            'data' : data,
            'rsync_data' : rsync_base_data,
            'system_info' : system_info,
            'ipmi_info' : ipmi_info
        }
        return res_data

    @rpc
    def systemrecover(self, data):
        logger.info("systemrecover: {}".format(data))

        #Get Target Image List
        target_image_list = self.db_send(method='GetTargetImageList', msg=data)
        logger.info('target_image_list : {}'.format(target_image_list))

        #Get IPMI Information
        ipmi_info = self.db_send(method='GetIPMIInfo', msg=data)
        logger.info('ipmi_info : {}'.format(ipmi_info))

        #Get System Information
        system_info = self.db_send(method='GetSystemInfo', msg=data)

        # Get snapshot list data [DbManager]
        snapshot_list = self.db_send(method='GetSnapshotList', msg=data)
        logger.info("systemrecover response : {}".format(snapshot_list))
        data['snapshot_list'] = snapshot_list

        for target in target_image_list:
            if target.get('dataset')[0:1].__eq__('/'):
                # Linux System
                data['dataset'] = target.get('dataset')
                rsync_base_data = self.db_send(method='GetRsyncData', msg=data)
                logger.info('rsync_base_data : {}'.format(rsync_base_data))
                if data.get('recover_type').__eq__('I'):
                    send_data = self.rsync_increment(data=data,rsync_base_data=rsync_base_data,
                                                     system_info=system_info, ipmi_info=ipmi_info)
                    res_data = self.service_send(method='rsyncrecover', msg=send_data, instance=self.backup_server_rpc)
                elif data.get('recover_type').__eq__('O'):
                    send_data = self.rsync_full(node_uuid=data.get('node_uuid'), rsync_base_data=rsync_base_data,
                                                     system_info=system_info, ipmi_info=ipmi_info)
                    res_data = self.service_send(method='rsyncfullrecover', msg=send_data, instance=self.backup_server_rpc)
            else:
                # Get MetaData [DbManager]
                find_list = []
                for snap_data in snapshot_list:
                    find_list.append(snap_data.get('snapshot_name'))
                data['snapshot_find_list'] = find_list
                snap_file_data = self.db_send(method='GetSnapImageList', msg=data)
                data['snap_file_data'] = snap_file_data
                # Check snapshot image file [FileManager]
                snap_file_data = self.service_send(method='check_snapshotImage', msg=snap_file_data,
                                                   instance=self.filemanager_rpc)
                logger.info("systemrecover snap_file_data : {}".format(snap_file_data))
                home_path = ""
                for file_data in snap_file_data:
                    dir_name_split = file_data.get('image_path').split('/')
                    for dir_name in dir_name_split:
                        if dir_name.__eq__(data.get('node_uuid')):
                            break
                        if len(dir_name) > 0:
                            home_path = "{}/{}".format(home_path, dir_name)
                    break

                logger.info("home_path : {}".format(home_path))

                if data.get('recover_type').__eq__('I'):
                    # Recover [Recover]
                    res_data = self.service_send(method='systemrecover', msg=data, instance=self.servicemanager_rpc)
                elif data.get('recover_type').__eq__('O'):
                    send_data = self.zfs_full(node_uuid=data.get('node_uuid'), snap_name=data.get('snapname'), home_path=home_path,
                             system_info=system_info, ipmi_info=ipmi_info)
                    logger.info("send_data {}".format(send_data))
                    res_data = self.service_send(method='zfsfullrecover', msg=send_data,
                                                 instance=self.backup_server_rpc)


        return res_data

    @rpc
    def setsystemhistory(self, data):
        logger.info("setsystemhistory: {}".format(data))
        if 'action_msg' in data:
            data['action_message'] = data['action_msg']
        if 'action_err_code' in data:
            data['err_code'] = data['action_err_code']
        if 'action_err_msg' in data:
            data['err_message'] = data['action_err_msg']
        response = self.db_send(method='processhistory', msg=data)
        return response

    # Get Backup & Recover & Error history
    @rpc
    def getsystemhistory(self, data):
        logger.info("getsystemhistory: {}".format(data))
        response = self.db_send(method='GetSystemHistory', msg=data)
        return response

    @rpc
    def getsystemprocesshistory(self, data):
        logger.info("getsystemhistory: {}".format(data))
        response = self.db_send(method='GetSystemProcessHistory', msg=data)
        return response

    @rpc
    def systembackup(self, data):
        logger.info("systembackup: {}".format(data))
        target_list = data['backup_target']
        rsync_backup = False
        zfs_backup = False
        for target_kind in target_list:
            if target_kind[0:1].__eq__('/'):
                rsync_backup = True
            else:
                zfs_backup = True

        response = self.db_send(method='GetSystemInfo', msg=data)

        if rsync_backup:
            data['os_type'] = response.get('os_type')
            data['os_name'] = response.get('os_name')
            data['ipaddress'] = response.get('ipaddress')
            logger.info("data : {}".format(data))
            if data.get('backup_type').__eq__('I'):
                res_data = self.service_send(method='rsyncbackup', msg=data, instance=self.backup_server_rpc)
            elif data.get('backup_type').__eq__('F'):
                res_data = self.service_send(method='rsyncfullbackup', msg=data, instance=self.backup_server_rpc)
            
        if zfs_backup:
            res_data = self.service_send(method='systembackup', msg=data, instance=self.servicemanager_rpc)

        return res_data

############################################ DATA SYNC #################################################

    @rpc
    def synccheck(self, data):
        # data : {'sync_proc': '', sync_name': timapni_base.constants.SYNC_NAME_NODE}
        logger.info("[SYNCCHECK] data : {}".format(data))
        # Check Sync Data (DB)
        response = self.db_send(method='synccheck', msg=data)
        # response : {'result':'true' or 'false'}
        return response

    @rpc
    def mastersync(self, data):
        logger.info("[MASTER ACCOUNT SYNC] data : {}".format(data))
        response = self.db_send(method='mastersync', msg=data)
        return response

    @rpc
    def masterinfo(self, data):
        logger.info("[MASTER INFORMATION] data : {}".format(data))
        response = self.db_send(method='masterinfo', msg=data)
        return response

############################################# Backup #####################################################
    # Get Target List


    # Backup Command
    @rpc
    def backupcmd(self, data):
        # {"uuid":"PHY NODE UUID", "usetype" : "ORIGIN, OS, DATA", "nodetype" : "MASTER, STORAGE, COMPUTE"
        # , "name" : "volume name"}
        res = self.proc_backup.run(data)
        return res