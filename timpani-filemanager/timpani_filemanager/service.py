import logging
import timpani_filemanager.constants
import os
import sys
import time
import json
import requests
import shutil
from nameko.rpc import rpc
from nameko.timer import timer

from .configuration.configuration_file_reader import ConfigrationFileReader
from .util.systemutil import Systemutil
from timpani_apimanager.process.status.delete import DeleteProc

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

class RestAppService(object):

    systemutil = Systemutil()
    config = ConfigrationFileReader()

    def __init__(self, moduletype):
        self.nodetype_url = "/v1/app/getbiosconfig"
        self.addservice_url = "/v1/app/addservice"
        self.keepalive_url = "/v1/app/keepalive"
        self.template_init_url = "/v1/bios/init"
        config = self.config.read_file()
        self.backup_host = config['GENERAL']['BACKUP_IP']
        self.backup_webport = config['GENERAL']['WEBPORT']
        self.node_uuid = None
        self.amqp_url = None
        self.nodetype = 'FILEMANAGER'
        self.prefix = None
        self.nicname = config['GENERAL']['BACKUP_NIC']
        self.moduletype = moduletype
        self.istemplate_init = False


    def rest_request(self, url, postdata):
        issuccess = False
        resdata = None
        try:
            response = requests.post(url, data=json.dumps(postdata), timeout=3)
            if response.status_code == 200:
                logger.info("response data : {}".format(response.json()['resultData']))
                resdata = response.json()['resultData']
                issuccess = True
                if 'errorcode' in resdata:
                    logger.info("Get Nodetype Faild")
                    issuccess = False
            else:
                logger.info("response data : {}".format(response))
        except Exception as e:
            logger.info("api gateway connection failed : {}".format(e))

        return issuccess, resdata

    def addservice(self):
        home_url = "http://{host}:{port}".format(host=self.backup_host, port=self.backup_webport)
        self.uuid = self.systemutil.getSystemUuid()
        ipaddress = self.systemutil.getIpAddress(self.nicname)
        self.pid = self.systemutil.getPid()
        macaddress = self.systemutil.getMacAddress(self.nicname)
        postdata = {'node_uuid': self.uuid, 'pid': self.pid, 'nodetype': self.nodetype,
                    'ipaddress': ipaddress, 'macaddress': macaddress,
                    'moduletype': self.moduletype}
        url = home_url + self.addservice_url
        issuccess, resdata = self.rest_request(url, postdata)
        if issuccess:
            self.modulename = resdata.get('modulename')
        return issuccess

    def keepalive(self):
        home_url = "http://{host}:{port}".format(host=self.backup_host, port=self.backup_webport)
        postdata = {'pid': self.pid, 'moduletype': self.moduletype}
        url = home_url + self.keepalive_url
        issuccess, resdata = self.rest_request(url, postdata)
        # if issuccess:
        #     self.modulename = resdata.get('modulename')
        return issuccess


class FileManager(object):
    max_retry = 60
    init_data = RestAppService(moduletype='filemanager')

    retry_cnt = 0
    while True:
        if not init_data.addservice():
            logger.info("MODULE SERVICE REGITER FAILED")
        else:
            break
        if retry_cnt == max_retry:
            logger.info("MODULE SERVICE REGITER RETRY FAILED")
            sys.exit()
        time.sleep(1)
        retry_cnt += 1

    name = init_data.modulename
    node_uuid = init_data.node_uuid

    backup_host = init_data.backup_host
    logger.debug("name : {}, node_uuid : {}".format(__name__, node_uuid))

    # init_data.template_init()

    @timer(interval=30)
    def keepalive(self):
        logger.debug("START KEEPALIVE")
        self.init_data.keepalive()

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


    def check_dir(self, dir):
        logger.info("check_dir : {}".format(dir))

        try:
            return os.path.isdir(dir)
        except OSError:
            return False

    def delete_dir(self, dir):
        if dir.__eq__('/'):
            logger.info("ROOT DIRECTORY DELETE TRY FAILED")
            return False
        shutil.rmtree(dir)
        return self.check_dir(dir)

    @rpc
    def deleteproc(self, data):
        proc = data.get('proc')
        dellist = data.get('dellist')
        export_path = data.get('export_path')

        if proc.__eq__(DeleteProc.FILECHECK.value[0]):
            logger.info("proc : {}".format(proc))
            for deldata in dellist:
                check_path = deldata.get('save_path')
                part_path = deldata.get('part_path')
                if 'zfs.gz' in check_path:
                    sp_check_path = check_path.split('/')
                    snap_del_path = export_path
                    for cnt in range(1, len(sp_check_path)-1):
                        snap_del_path += '/' + sp_check_path[cnt]
                    logger.info('snap_del_path : {}'.format(snap_del_path))

                    deldata['snap_del_path'] = snap_del_path
                    deldata['issnapdelexist'] = self.check_dir(snap_del_path)
                else:
                    deldata['snap_del_path'] = export_path + check_path
                    deldata['issnapdelexist'] = self.check_dir(check_path)
                deldata['part_del_path'] = export_path + part_path
                deldata['ispartdelexist'] = self.check_dir(export_path + part_path)

        elif proc.__eq__(DeleteProc.SNAPDIRDELETE.value[0]):
            logger.info("proc : {}".format(proc))
            for deldata in dellist:
                logger.info('SNAP FILE DELETE DIR : {}'.format(deldata.get('snap_del_path')))
                logger.info('SNAP DELETE DIR EXIST : {}'.format(deldata.get('issnapdelexist')))
                del_path = deldata.get('snap_del_path')
                isdelexist = deldata.get('issnapdelexist')
                if isdelexist:
                    self.delete_dir(del_path)

        elif proc.__eq__(DeleteProc.PARTDIRDELETE.value[0]):
            logger.info("proc : {}".format(proc))
            for deldata in dellist:
                logger.info('PART DELETE DIR : {}'.format(deldata.get('part_del_path')))
                logger.info('PART DELETE DIR EXIST : {}'.format(deldata.get('ispartdelexist')))
                del_path = deldata.get('part_del_path')
                isdelexist = deldata.get('ispartdelexist')
                if isdelexist:
                    self.delete_dir(del_path)

        return data



