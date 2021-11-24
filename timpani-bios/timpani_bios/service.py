import logging
import time
import requests
import json
import sys
import timpani_bios.constants
from nameko.rpc import rpc
from nameko.timer import timer

from timpani_apimanager.process.status.bios import BiosProc

from timpani_bios.configuration.configuration_file_reader import ConfigrationFileReader
from timpani_bios.configuration.config_set import ConfigSetting
from timpani_bios.configuration.register_service import RegisterService
from timpani_bios.transfer import TransferServiceManager
from .util.systemutil import Systemutil
from .syscfg.biosconfig import BiosConfig
from .setting.templeate import Template
from .model.proc import ProcModel
from .util.sdptool import SDPTool
from .util.ipmitool import IpmiTool
from .transfer import TransferServiceManager


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
        self.nodetype = 'IPMI'
        self.prefix = None
        self.nicname = None
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

    def getnodetype(self):
        home_url = "http://{host}:{port}".format(host=self.backup_host, port=self.backup_webport)
        self.uuid = self.systemutil.getSystemUuid()
        postdata = {'node_uuid': self.uuid}
        url = home_url + self.nodetype_url
        issuccess, resdata = self.rest_request(url, postdata)
        if issuccess:
            self.nodetype = resdata.get('nodetype')
            self.prefix = resdata.get('configdata').get('prefix')
            self.nicname = resdata.get('configdata').get('nicname')
            config_data_rabbit_id = resdata.get('configdata').get('rabbit_id')
            config_data_rabbit_pass = resdata.get('configdata').get('rabbit_pass')
            config_data_rabbit_port = resdata.get('configdata').get('rabbit_port')
            self.amqp_url = "amqp://{id}:{passwd}@{host}:{port}".\
                format(id=config_data_rabbit_id, passwd=config_data_rabbit_pass,
                       host=self.backup_host, port=config_data_rabbit_port)
            timpani_bios.constants.AMQP_CONFIG = {}
            timpani_bios.constants.AMQP_CONFIG['AMQP_URI'] = self.amqp_url
        return issuccess

    def addservice(self):
        home_url = "http://{host}:{port}".format(host=self.backup_host, port=self.backup_webport)
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

    def templateinit(self, postdata):
        if self.istemplate_init:
            return True

        home_url = "http://{host}:{port}".format(host=self.backup_host, port=self.backup_webport)
        url = home_url + self.template_init_url
        issuccess, resdata = self.rest_request(url, postdata)
        if issuccess:
            self.istemplate_init = True
        #     self.modulename = resdata.get('modulename')
        return issuccess

    def template_init(self):

        if self.istemplate_init:
            return True
        # Template Init
        template_class = Template()
        template_ini_home = '/etc/timpani/bios'

        # read templeate
        template = template_class.read(template_ini_home + '/bios_template.ini')
        template_val = template_class.read_definevalue(template_ini_home + '/bios_template_value.ini')
        match_data = template_class.read_match(template_ini_home + '/bios_match_key.ini')
        template_data = template_class.template_setting_data(template, template_val)
        postdata = {'avail_data': template_val, 'match_data': match_data, 'template_data': template_data}
        logger.info("template_init post_data : \n{}".format(postdata))
        self.templateinit(postdata)


class BiosService(object):
    max_retry = 60
    init_data = RestAppService(moduletype='bios')
    retry_cnt = 0
    while True:
        if not init_data.getnodetype():
            logger.info("MODULE SERVICE REGITER FAILED")
        else:
            break

        if retry_cnt == max_retry:
            logger.info("MODULE SERVICE REGITER RETRY FAILED")
            sys.exit()
        time.sleep(1)
        retry_cnt += 1

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
    amqp_url = init_data.amqp_url
    logger.debug("name : {}, node_uuid : {}".format(__name__, node_uuid))

    trans = TransferServiceManager()
    # init_data.template_init()

    @timer(interval=30)
    def keepalive(self):
        logger.debug("START KEEPALIVE")
        self.init_data.keepalive()
        time.sleep(1)
        self.init_data.template_init()
        res = self.trans.api_send('sensorcollect', msg=None)


    @rpc
    def template_init(self, data):
        # Template Init
        template_class = Template()
        template_ini_home = '/etc/timpani/bios'

        # read templeate
        template = template_class.read(template_ini_home + '/bios_template.ini')
        template_val = template_class.read_definevalue(template_ini_home + '/bios_template_value.ini')
        match_data = template_class.read_match(template_ini_home + '/bios_match_key.ini')
        template_data = template_class.template_setting_data(template, template_val)
        return {'avail_data': template_val, 'match_data': match_data, 'template_data': template_data}

    @rpc
    def test(self,data):
        return data

    def sensor(self, host, user, passwd, macaddr, target_uuid):
        ipmitool = IpmiTool()
        sdptool = SDPTool()
        keylist = ['sensor_name', 'sensor_value', 'sensor_units', 'sensor_state',
                   'sensor_lo_norec', 'senor_lo_crit', 'sensor_lo_nocrit',
                   'senosr_up_nocrit', 'sensor_up_crit', 'sensor_up_norec']

        output = ipmitool.sensor(host=host, user=user, passwd=passwd)
        lines = output.split('\n')
        sensordatalist = []
        for line in lines:
            isparse = True
            if 'discrete' in line:
                isparse = False

            if isparse:
                values = line.split('|')
                cnt = 0
                sensordata = {}
                for v in values:
                    if 'na' in v:
                        val = None
                    else:
                        val = v.replace('\t', '').strip()
                    k_cnt = 0
                    for k in keylist:
                        if k_cnt == cnt:
                            if k.__eq__('sensor_value'):
                                if val is None:
                                    sensordata[k] = 0.0
                                else:
                                    sensordata[k] = float(val)
                            else:
                                sensordata[k] = val
                            break
                        k_cnt += 1
                    cnt += 1
                sensordatalist.append(sensordata)

        output = sdptool.sensor(host=host, user=user, passwd=passwd)
        lines = output.split('\n')
        for line in lines:
            values = line.split(' ')
            sensordata = {}
            cnt = 0
            k_cnt = 0
            for k in keylist:
                v_cnt = 0
                v_val = None
                for v in values:
                    if k_cnt == v_cnt:
                        if k_cnt == 0:
                            v_val = "Power " + v
                        else:
                            v_val = v
                    v_cnt += 1
                sensordata[k] = v_val
                k_cnt += 1
            if len(values) > 1:
                sensordatalist.append(sensordata)

        for target in sensordatalist:
            target['macaddr'] = macaddr
            target['addr'] = host
            target['node_name'] = target_uuid

        return sensordatalist

    @rpc
    def getsensor(self, data):
        logger.info("===================== [getsensor] =========================")
        ipmilist = data.get('ipmilist')
        sensordatalist = []
        for ipmidata in ipmilist:
            user = ipmidata.get('user')
            passwd = ipmidata.get('passwd')
            host = ipmidata.get('ip')
            macaddr = ipmidata.get('macaddr')
            target_uuid = ipmidata.get('target_uuid')
            sensordata = self.sensor(host=host, user=user, passwd=passwd, macaddr=macaddr, target_uuid=target_uuid)
            sensordatalist.append(sensordata)
        data['sensordatalist'] = sensordatalist

        return data

    @rpc
    def biosproc(self, data):
        proc = data.get('proc')

        if proc.__eq__(BiosProc.IPMICHECK.value[0]):
            data = ProcModel.ipmicheck(data)
            data = ProcModel.getsysteminfo(data)
        elif proc.__eq__(BiosProc.TEMPLATEDEPLOY.value[0]):
            data = ProcModel.templatedeploy(data)
        elif proc.__eq__(BiosProc.IPMIPOWERON.value[0]):
            data = ProcModel.ipmipoweron(data)
        elif proc.__eq__(BiosProc.IPMIPOWERSTATUS.value[0]):
            data = ProcModel.ipmipowerstatus(data)
        elif proc.__eq__(BiosProc.SYSCFGPATCH.value[0]):
            data = ProcModel.syscfgpatch(data)
        elif proc.__eq__(BiosProc.SYSCFGDUMP.value[0]):
            data = ProcModel.syscfgdump(data)
        elif proc.__eq__(BiosProc.SYSCFGBACKUP.value[0]):
            data = ProcModel.syscfgbackup(data)
        elif proc.__eq__(BiosProc.REQISCSIOFF.value[0]):
            data = ProcModel.reqiscsioff(data)
        elif proc.__eq__(BiosProc.CHECKBIOSVALUE.value[0]):
            data = ProcModel.checkbiosvalue(data)
        elif proc.__eq__(BiosProc.BIOSDATACOLLECT.value[0]):
            data = ProcModel.biosdatacollect(data)
        elif proc.__eq__(BiosProc.NFSMOUNT.value[0]):
            data = ProcModel.nfsmount(data)
        elif proc.__eq__(BiosProc.NFSUNMOUNT.value[0]):
            data = ProcModel.nfsunmount(data)

        return data

