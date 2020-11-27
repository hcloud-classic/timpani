# from .filemanager_pb2 import ActionResponse, ResgisterResponse
# from .filemanager_pb2_grpc import FilemangerServiceStub
# 
# from timpani_framework.grpc.entrypoint import Grpc
# from google.protobuf import json_format
# import json
# 
# grpc = Grpc.implementing(FilemangerServiceStub)
# 
# 
# # ActionRequest
# # int32 action = 1;
# # int32 msgid = 2;
# # string method = 3;
# # google.protobuf.Struct message = 4;
# 
# class FileManagerService:
#     name = 'filemanager_service'
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
#     # @grpc
#     # def register(self, request, context):
#     #     return ResgisterResponse()

# import eventlet
# import errno
# import time
# from timpani_framework.runner import run_services
#
# def main():
#     config={}
#     api = ApiManagerService()
#
#     service_runner = run_services(config, api)
#
#     while True:
#         try:
#             time.sleep(60)
#         except KeyboardInterrupt:
#             print()
#             try:
#                 service_runner.stop()
#             except KeyboardInterrupt:
#                 print()
#                 service_runner.kill()
#
#             else:
#             # runner.wait completed
#                 break
#
# if __name__=="__main__":
#     main()

import logging
import timpani_filemanager.constants
import os
import sys
from nameko.rpc import rpc

from timpani_filemanager.configuration.configuration_file_reader import ConfigrationFileReader
from timpani_filemanager.configuration.config_set import ConfigSetting
from timpani_filemanager.configuration.register_service import RegisterService
from timpani_filemanager.transfer import TransferServiceManager



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
        import timpani_filemanager.constants
        config = ConfigrationFileReader()
        config_set = ConfigSetting(config.read_file())
        config_set.setConfig()
        self.service_manager_trans = TransferServiceManager(timpani_filemanager.constants.AMQP_CONFIG)
        service_data = RegisterService(node_uuid=timpani_filemanager.constants.NODE_UUID,
                                   capability=timpani_filemanager.constants.CAPABILITY,
                                   ipv4address=timpani_filemanager.constants.SERVICE_IPV4ADDR)

        # get Agent ID
        res_data = self.service_manager_trans.send(method="registerService", service_name='service_manager' ,msg=service_data.__dict__)
        if 'agent_id' in res_data.keys():
            timpani_filemanager.constants.AGENT_ID = res_data.get('agent_id')
        else:
            logger.info("GET Agent KEY FAILED")
            exit()

        self.node_uuid = timpani_filemanager.constants.NODE_UUID
        self.agent_id = timpani_filemanager.constants.AGENT_ID
        self.address = timpani_filemanager.constants.SERVICE_IPV4ADDR
        self.base_url = timpani_filemanager.constants.BASE_STORAGE_URI
        self.service_name = "{}_service_{}".format(timpani_filemanager.constants.CAPABILITY, timpani_filemanager.constants.NODE_UUID)

    def service_send(self, method, msg):
        ret = self.service_manager_trans.send(method=method, service_name='service_manager', msg=msg)
        return ret

class FileManager(object):
    init_data = ServiceInit()
    name = init_data.service_name
    node_uuid = init_data.node_uuid
    agent_id = init_data.agent_id
    ip_address = init_data.address
    send_service = init_data.service_send
    backup_base = "{}/backup".format(init_data.base_url)
    logger.info("name : {}, node_uuid : {}, agent_id : {}".format(__name__, node_uuid, agent_id))

    @rpc
    def check_directory(self, data):
        node_uuid = data.get('node_uuid')
        check_url = "{}/{}".format(self.backup_base, node_uuid)
        res_data = {'result': '0000', 'resultMsg': 'Success'}
        try:
            if not os.path.isdir(check_url):
                os.makedirs(check_url)
        except OSError:
            res_data = {'errcode':'9001', 'errorstr':'Creating directory Failed = {}'.format(check_url)}

        return res_data


        

    # @rpc
    # def scp_app1(self, image_path):
    #     logger.info("============== SCP APP1 SENDER [WEB] ===========")
    #     ip = self.config.GetConfig(self.CONFIG_NAME, 'app1_ip')
    #     port = self.config.GetConfig(self.CONFIG_NAME, 'app1_port')
    #     user = self.config.GetConfig(self.CONFIG_NAME, 'app1_user')
    #     password = self.config.GetConfig(self.CONFIG_NAME, 'app1_pass')
    #
    #     try:
    #         ssh = SSHClient()
    #         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #         ssh.connect(ip, port=port, username=user, password=password)
    #     except paramiko.AuthenticationException:
    #         logger.info("Authentication failed, please verify your credentials")
    #     except paramiko.SSHException as sshException:
    #         logger.info("Unable to establish SSH Connection : %s" % sshException)
    #     except paramiko.BadHostKeyException as badHostKeyException:
    #         logger.info("Unable to verify server's host key : %s" % badHostKeyException)
    #     except Exception as e:
    #         logger.info(e.args)
    #
    #     src_path_root = self.config.GetConfig(self.CONFIG_NAME, 'src_path_root')
    #     dest_path_root = self.config.GetConfig(self.CONFIG_NAME, 'dest_path_root')
    #     image_path_root = self.config.GetConfig(self.CONFIG_NAME, 'image_path_root')
    #     img_path, file_name = os.path.split(image_path)
    #     src_path = src_path_root + '/' + image_path_root + image_path
    #     dest_path = dest_path_root + '/' + image_path_root + img_path
    #     logger.info(
    #         "src_path_root : {}\n dest_path_root : {}\n image_path_root : {}\n".format(src_path_root, dest_path_root,
    #                                                                                    image_path_root))
    #     logger.info("src_path : {} dest_path : {}".format(src_path, dest_path))
    #     ssh.exec_command('mkdir -p ' + dest_path)
    #
    #     scp = SCPClient(ssh.get_transport())
    #     scp.put(src_path, recursive=True, remote_path=dest_path)
    #     scp.close()
    #     ssh.close()

