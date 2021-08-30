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
import platform
import timpani_system.constants
from nameko.rpc import rpc
from nameko.timer import timer

from timpani_system.configuration.configuration_file_reader import ConfigrationFileReader
from timpani_system.configuration.config_set import ConfigSetting
from timpani_system.configuration.register_service import RegisterService
from timpani_system.transfer import TransferServiceManager
from timpani_system.resource import ResourceSystem
from . import metadata
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
                                       ipv4address=timpani_system.constants.SERVICE_IPV4ADDR,
                                       pid = timpani_system.constants.SERVICE_PID,
                                       macaddress=timpani_system.constants.SERVICE_MACADDR)
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
        self.macaddress = timpani_system.constants.SERVICE_MACADDR
        self.service_name = "{}_service_{}".format(timpani_system.constants.CAPABILITY, timpani_system.constants.NODE_UUID)

    def service_send(self, method, msg):
        ret = self.service_manager_trans.send(method=method, service_name='service_manager', msg=msg)
        return ret

class SystemService(object):

    init_data = ServiceInit()
    name = init_data.service_name
    node_uuid = init_data.node_uuid
    agent_id = init_data.agent_id
    ip_address = init_data.address
    send_service = init_data.service_send
    logger.info("name : {}, node_uuid : {}, agent_id : {}".format(__name__, node_uuid, agent_id))

    # Register System base information
    base_info = ResourceSystem.getBaseInformation()
    base_info['ipv4address'] = timpani_system.constants.SERVICE_IPV4ADDR
    base_info['node_uuid'] = node_uuid
    logger.info("Base System Info : {}".format(base_info))
    system_id = send_service(method="registerSystemInfo", msg=base_info)
    logger.info("Sytem ID : {}".format(system_id))

    # pid = os.getpid()

    def return_success(self, result):
        return {'node_uuid': self.node_uuid, 'agent_id' : self.agent_id, 'result' : result}

    @timer(interval=30)
    def get_zfslist(self):
        res_list = None
        if not platform.system() == 'FreeBSD':
            check_user_dirs = ResourceSystem.CheckUserHome()
            check_mnt = ResourceSystem.CheckMountDirectory()
            for mnt in check_mnt:
                if not mnt['mountpoint'].__eq__('/'):
                    check_user_dirs.append(mnt['mountpoint'].replace('"','').replace('}',''))

            for mp in check_user_dirs:
                name,used,avail,refer,mountp = ResourceSystem.getSystemDiskFree(mp)
                if res_list is None:
                    res_list = []
                save_data = {'zfs_ref_size': refer, 'zfs_type': 'dir', 'zfs_used_size': used, 'zfs_mount_point': mountp, 'zfs_avail_size': avail, 'zpool_name': 'linux', 'zfs_name': mountp }
                res_list.append(save_data)

        logger.info("check dirs : {}".format(res_list))

        if ResourceSystem.CheckZFS():
            result = ResourceSystem.GetBackupSrcList(res_list)
            response_data = self.return_success(result)
            self.send_service(method="SetBackupSrcList", msg=response_data)
        else:
            response_data = self.return_success(res_list)
            self.send_service(method="SetBackupSrcList", msg=response_data)


