import logging
import logging.handlers
import re
import datetime
from ..util.ipmitool import IpmiTool
from ..util.sdptool import SDPTool
from ..util.mount import MountUtil
from ..util.systemutil import Systemutil
from ..syscfg.createsyscfg import CreateSysCfg
from ..syscfg.biosconfig import BiosConfig
from ..constants import BIOSCONFIGFILE, REDFISH_BIOSCONFIGFILE

################################### logger ############################################################################
logger = logging.getLogger(__name__)
#logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
fileHandler = logging.handlers.TimedRotatingFileHandler(filename='./log_'+__name__.__str__(), when='midnight', backupCount=0, interval=1, encoding='utf-8')
fileHandler.setFormatter(formatter)
fileHandler.setLevel(level=logging.INFO)
logger.addHandler(fileHandler)
# stream_hander = logging.StreamHandler()
# stream_hander.setFormatter(formatter)
# stream_hander.setLevel(level=logging.INFO)
# logger.addHandler(stream_hander)
#######################################################################################################################


class ProcModel(object):

    @staticmethod
    def getNowStr(kind):
        now = datetime.datetime.now()
        nowDate = now.strftime('%Y%m%d%H%M%S')
        day = nowDate[:8]
        time = nowDate[8:]
        backupname = kind+nowDate
        getini_filename = 'getini_syscfg' + "_" + backupname + ".INI"
        redfish_filename = 'syscfg' + "_" + backupname + ".INI"
        return getini_filename, redfish_filename, backupname

    @staticmethod
    def getipmiconnectinfo(data):
        user = data.get('ipmi').get('user')
        pw = data.get('ipmi').get('passwd')
        addr = data.get('ipmi').get('ip')
        return user, pw, addr

    @staticmethod
    def strmatch(src, target):
        pattern = re.compile(target)
        if pattern.search(src):
            return True
        return False

    @staticmethod
    def ipmicheck(data):
        ipmitool = IpmiTool()
        user, pw, addr = ProcModel.getipmiconnectinfo(data)
        res = ipmitool.guid(host=addr, user=user, passwd=pw)
        # logger.info("ipmicheck : {}".format(res))
        sp_line = res.split("\n")
        guid = None
        for line in sp_line:
            word = line.split(":")
            if 'GUID' in word[0]:
                guid = word[1].strip()

        data['guid'] = guid
        if guid is None:
            data['isipmicheck'] = False
        else:
            data['isipmicheck'] = True

        return data

    @staticmethod
    def getsysteminfo(data):
        sdptool = SDPTool()
        user, pw, addr = ProcModel.getipmiconnectinfo(data)
        result = sdptool.systeminfo(host=addr, user=user, passwd=pw)
        logger.info("[getsysteminfo] result : {}".format(result))
        sp_res = result.split('\n')

        bios_ver = None
        me_ver = None
        sdr_ver = None
        bmc_ver = None

        for line in sp_res:
            if ProcModel.strmatch(line, 'BIOS'):
                bios_ver = line.split(':')[1].strip()
            elif ProcModel.strmatch(line, 'ME'):
                me_ver = line.split(':')[1].strip()
            elif ProcModel.strmatch(line, 'SDR'):
                sdr_ver = line.split(':')[1].strip()
            elif ProcModel.strmatch(line, 'BMC'):
                bmc_ver = line.split(':')[1].strip()

        data['sys_bios_ver'] = bios_ver
        data['sys_me_ver'] = me_ver
        data['sys_sdr_ver'] = sdr_ver
        data['sys_bmc_ver'] = bmc_ver
        return data

    @staticmethod
    def ipmipoweron(data):
        ipmitool = IpmiTool()
        user, pw, addr = ProcModel.getipmiconnectinfo(data)
        res = ipmitool.powerstatus(host=addr, user=user, passwd=pw)
        ison = ProcModel.strmatch(res, 'failed')
        data['is_poweron'] = not ison
        return data

    @staticmethod
    def ipmipoweroff(data):
        ipmitool = IpmiTool()
        user, pw, addr = ProcModel.getipmiconnectinfo(data)
        res = ipmitool.powerstatus(host=addr, user=user, passwd=pw)
        isoff = ProcModel.strmatch(res, 'failed')
        data['is_poweroff'] = not isoff
        return data

    @staticmethod
    def ipmipowerstatus(data):
        ipmitool = IpmiTool()
        user, pw, addr = ProcModel.getipmiconnectinfo(data)
        res = ipmitool.powerstatus(host=addr, user=user, passwd=pw)
        ison = ProcModel.strmatch(res, 'on')

        data['is_powerstatus'] = ison
        return data

    @staticmethod
    def templatedeploy(data):
        sdptool = SDPTool()
        user, pw, addr = ProcModel.getipmiconnectinfo(data)
        syscfg_path = data.get('src_path')
        result = sdptool.deployoptions(host=addr, user=user, passwd=pw, syscfg_path=syscfg_path)
        logger.info("[templatedeploy] result : {}".format(result))
        sp_res = result.split('\n')
        isres = True
        for line in sp_res:
            iserror = ProcModel.strmatch(line, 'Error')
            if iserror:
                isres = False
        if isres:
            data['is_templatedeploy'] = isres
        return data

    @staticmethod
    def syscfgpatch(data):
        syscfg = CreateSysCfg()
        setname = data.get('name')
        match_kind = data.get('match_kind')

        if data.get('biosconfig') is None:
            data['iserror'] = True
            return data

        getinisyscfg = data.get('biosconfig').get('syscfg_filename')
        matchdata = data.get('templatedata').get('match_data')
        templatedata = data.get('templatedata').get('template_data')
        templatevalue = data.get('templatedata').get('avail_data')
        mount_path = data.get('mount_path')
        macaddr = data.get('ipmi').get('macaddr')
        macdir = macaddr.replace(':', '')
        syscfg_path = "/bios/" + macdir
        orig_path = mount_path + syscfg_path + '/' + getinisyscfg

        replace_data = syscfg.replace_template_data(setname, match_kind, templatedata, matchdata)
        getini_filename, redfish_filename, backupname, target_path = syscfg.create_template_syscfg(setname, syscfg_path, mount_path, orig_path, replace_data)
        data['replace_data'] = replace_data
        data['src_path'] = target_path
        data['redfish_target_path'] = mount_path + syscfg_path + '/' + redfish_filename
        return data

    @staticmethod
    def redfishdump(data):
        sdptool = SDPTool()
        user, pw, addr = ProcModel.getipmiconnectinfo(data)
        # save path create
        result = sdptool.getbiosconfigall(host=addr, user=user, passwd=pw)
        sp_res = result.split('\n')
        log_dir = None
        for line in sp_res:
            iserror = ProcModel.strmatch(line, 'Error')
            islogdir = ProcModel.strmatch(line, 'generated')

            if iserror:
                break
            if islogdir:
                log_dir = line.split(":")[2].strip()

        if iserror:
            errcode = "7010"
            errmsg = "Bios Dump Failed"
            return {'err_code': errcode, 'err_message': errmsg}

        data['log_dir'] = log_dir
        data['redfish_src_path'] = log_dir + '/' + REDFISH_BIOSCONFIGFILE

        return data


    @staticmethod
    def syscfgdump(data):
        sdptool = SDPTool()
        user, pw, addr = ProcModel.getipmiconnectinfo(data)
        # save path create
        result = sdptool.getini(host=addr, user=user, passwd=pw)
        sp_res = result.split('\n')
        log_dir = None
        for line in sp_res:
            iserror = ProcModel.strmatch(line, 'Error')
            islogdir = ProcModel.strmatch(line, 'generated')

            if iserror:
                break
            if islogdir:
                log_dir = line.split(":")[2].strip()

        if iserror:
            errcode="7010"
            errmsg = "Bios Dump Failed"
            return {'err_code': errcode, 'err_message':errmsg}

        data['log_dir'] = log_dir
        data['src_path'] = log_dir + '/' + BIOSCONFIGFILE

        data = ProcModel.redfishdump(data)

        return data

    @staticmethod
    def syscfgbackup(data):
        return data

    @staticmethod
    def checkbiosvalue(data):
        syscfg = CreateSysCfg()
        data = ProcModel.redfishdump(data)
        replace_list = data.get('replace_data')
        target_path = data.get('redfish_target_path')
        src_path = data.get('redfish_src_path')
        logger.info("replace_data : {} \n".format(replace_list))
        logger.info("target_path : {} \n".format(target_path))
        logger.info("src_path : {} \n".format(src_path))
        isvalid = syscfg.vaild_setting_data_syscfgmove(src_path=src_path, target_path=target_path, replace_list=replace_list)
        data['patch_isvalid'] = isvalid
        if isvalid:
            logger.info(" \n========================= TEMPLATE SETTING SUCCESS =========================\n ")
        else:
            logger.info(" \n========================= TEMPLATE SETTING FAILED =========================\n ")
        return data

    @staticmethod
    def reqiscsioff(data):
        return data

    @staticmethod
    def nfsmount(data):
        util = MountUtil()
        nfs_server = data.get('nfs_server')
        export_path = data.get('export_path')
        mount_path = data.get('mount_path')
        if export_path.__eq__(mount_path):
            mount_path = mount_path + '_backup'
        data['mount_path'] = mount_path
        devicelist, isnfsmount = util.nfsmount(nfs_server, export_path, mount_path)
        return data

    @staticmethod
    def nfsunmount(data):
        util = MountUtil()
        nfs_server = data.get('nfs_server')
        export_path = data.get('export_path')
        mount_path = data.get('mount_path')
        isnfsmount = util.nfsumount(nfs_server, mount_path)
        return data

    @staticmethod
    def biosdatacollect(data):
        syscfg = CreateSysCfg()
        config = BiosConfig()
        src_path = data.get('src_path')
        redfish_src_path = data.get('redfish_src_path')
        mount_path = data.get('mount_path')
        macaddr = data.get('ipmi').get('macaddr')
        macdir = macaddr.replace(':', '')
        syscfg_path = "/bios/" + macdir
        guid = data.get('guid')
        runkind = data.get('runkind')
        templatedata = data.get('templatedata')

        if runkind.__eq__('dump'):
            replace_list = None
        else:
            replace_list = data.get('replace_list')

        avail_data = templatedata.get('avail_data')
        match_data = templatedata.get('match_data')
        template_data = templatedata.get('template_data')

        syscfg_filename, redfish_filename, backupname = ProcModel.getNowStr(runkind)

        # Directory Check
        systemutil = Systemutil()
        systemutil.dirExistCheckAndCreate(mount_path+syscfg_path)

        # Template Data Collect
        target_path = mount_path+syscfg_path+'/'+syscfg_filename
        redfish_target_path = mount_path + syscfg_path + '/' + redfish_filename
        templatedatalist, template_name = syscfg.movecfg(src_path=src_path, target_path=target_path,
                                                         avail_data=avail_data, match_data=match_data,
                                                         template_data=template_data, guid=guid, macaddr=macaddr)

        # Template Set Vailed Check and File Backup
        istemplatematch = syscfg.vaild_setting_data_syscfgmove(src_path=redfish_src_path,
                                                               target_path=redfish_target_path,
                                                               replace_list=replace_list)

        # BiosConfig Data Read
        syscfgdatalist = config.getini_read(src_path=src_path, guid=guid, macaddr=macaddr)
        backupdata = {
            'kind': runkind,
            'sys_bios_ver': data.get('sys_bios_ver'),
            'sys_me_ver': data.get('sys_me_ver'),
            'sys_sdr_ver': data.get('sys_sdr_ver'),
            'sys_bmc_ver': data.get('sys_bmc_ver'),
            'template_name': template_name,
            'macaddr': macaddr,
            'guid': guid.upper().replace('-', ''),
            'backupname':backupname,
            'syscfg_path':syscfg_path,
            'syscfg_filename':syscfg_filename,
            'redfish_filename':redfish_filename
            }

        data['biosdata'] = {'backupdata': backupdata, 'biosconfig': syscfgdatalist, 'template': templatedatalist}

        return data

