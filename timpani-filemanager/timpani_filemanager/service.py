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
    name = 'filemanager_service'
    node_uuid = init_data.node_uuid
    agent_id = init_data.agent_id
    ip_address = init_data.address
    send_service = init_data.service_send
    backup_base = "{}/backup".format(init_data.base_url)
    logger.info("name : {}, node_uuid : {}, agent_id : {}".format(__name__, node_uuid, agent_id))

    @rpc
    def check_directory(self, data):
        logger.info("check_directory : {}".format(data))
        node_uuid = data.get('node_uuid')
        check_list = data.get('check_dirs')
        for check_dir in check_list:
            check_url = "{}".format(check_dir)
            res_data = {'result': '0000', 'resultMsg': 'Success'}
            try:
                if not os.path.isdir(check_url):
                    os.makedirs(check_url)
            except OSError:
                res_data = {'errcode':'9001', 'errorstr':'Creating directory Failed = {}'.format(check_url)}

        return res_data


    @rpc
    def check_filesize(self, data):
        node_uuid = data.get('node_uuid')
        check_file = data.get('check_file')
        logger.info('[check_filesize] check_file : {}'.format(check_file))
        try:
            stat = os.stat(check_file)
            f_size = stat.st_size
        except:
            f_size = -1

        return {'file_size': f_size}


    @rpc
    def check_snapshotImage(self, data):
        for check_data in data:
            check_path = check_data.get('image_path')

            if os.path.isfile(check_path):
                stat = os.stat(check_path)
                f_size = stat.st_size
                check_size = int(check_data.get('image_size'))
                if f_size is check_size:
                    check_data['is_exist'] = True
                else:
                    check_data['is_exist'] = False
            else:
                check_data['is_exist'] = False

        return data

