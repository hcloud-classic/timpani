import logging
import click
from .syscfg.biosconfig import BiosConfig
from .syscfg.createsyscfg import CreateSysCfg
from .setting.templeate import Template
from .model.proc import ProcModel
from .util.ipmitool import IpmiTool
from .util.sdptool import SDPTool

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


def test():
    print("[INIT] Send BIOS Configuration Info")
    bios = BiosConfig()
    bios_config_info = bios.read_syscfg("test_syscfg.INI")
    print(bios_config_info)

def sensor():
    data['ipmi'] = {'user': 'root', 'passwd': '123123', 'ip': '172.32.100.53'}
    ipmitool = IpmiTool()
    sdptool = SDPTool()

    keylist = ['sensor_name','sensor_value','sensor_units', 'sensor_state',
               'sensor_lo_norec', 'senor_lo_crit', 'sensor_lo_nocrit',
               'senosr_up_nocrit', 'sensor_up_crit','sensor_up_norec']

    host = "172.32.100.53"
    user = "root"
    passwd = "123123"
    output = ipmitool.sensor(host=host, user=user, passwd=passwd)
    lines = output.split('\n')
    sensorlist = []
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
                        sensordata[k] = val
                        break
                    k_cnt += 1
                cnt += 1
            if len(values) > 1:
                sensorlist.append(sensordata)
    print("sensor data : {}".format(sensorlist))

    #output = sdptool.sensor(host=host, user=user, passwd=passwd)
    #lines = output.split('\n')



@click.command()
@click.option('--template', default="./bios_template.ini", help='bios templeate file path')
@click.option('--valuedefine', default="./bios_template_value.ini", help='redfish setting value define file')
@click.option('--matchdefine', default="./bios_match_key.ini", help='redfish and syscfg key value match define file')
@click.option('--setname', default="HPC1", help='Setting Template name')
@click.option('--orig_syscfg', default="./getini_syscfg.INI", help="orignal syscfg file name")
def bios_test(template, valuedefine, matchdefine, setname, orig_syscfg):
    print("templeate path : {}".format(template))
    templeate_class = Template()

    # read templeate
    read_data = templeate_class.read(template)
    read_valuedefine = templeate_class.read_definevalue(valuedefine)
    read_match = templeate_class.read_match(matchdefine)
    template_data = templeate_class.template_setting_data(read_data, read_valuedefine)
    print("templeate read data: {}\n\n".format(read_data))
    print("value defined read data: {}\n\n".format(read_valuedefine))
    print("match read data: {}\n\n".format(read_match))
    print("templeate setting data: {}\n\n".format(template_data))

    res_data = {'avail_data':read_valuedefine, 'match_data':read_match, 'template_data':template_data}
    data['gettemplatedata'] = res_data
    data['match_kind'] = 'Default'
    data['name'] = 'Default1'
    data['mount_path'] = '/nfsroot'
    data['biosconfig'] = {
        'match_kind':'Default', 'templeate_name':'Default2',
        'target_uuid':'targetuuid', 'ipaddr':'172.32.100.53',
        'syscfg_path':'/bios/guid',
        'getini_syscfg_filename':'getini_syscfg_20211011132456.INI',
        'redfish_syscfg_filename':'syscfg_20211011132456.INI',
        'ipmi_guid':'guid'
    }
    data['ipmi'] = {'user':'root', 'passwd':'123123', 'ip':'172.32.100.53'}
    test = test_biosproc()
    test.dump(data)

    # Make Template Syscfg
    # syscfg = CreateSysCfg()
    # replace_data = syscfg.replace_template_data(setname, "Default", read_data, read_match)
    # print("replace data : {}".format(replace_data))
    # new_path = syscfg.create_template_syscfg(setname, orig_syscfg, replace_data)
    # print("create new syscfg : {}".format(new_path))
    return res_data


class test_biosproc(object):

    def ipmicheck(self, data):
        data = ProcModel.ipmicheck(data)
        data = ProcModel.getsysteminfo(data)
        return data

    def ipmipowerstatus(self, data):
        data = ProcModel.ipmipowerstatus(data)
        return data

    def reqiscsioff(self, data):
        data = ProcModel.reqiscsioff(data)
        return data

    def syscfgdump(self, data):
        data = ProcModel.syscfgdump(data)
        return data

    def nfsmount(self, data):
        data = ProcModel.nfsmount(data)
        return data

    def biosdatacollect(self, data):
        data = ProcModel.biosdatacollect(data)
        return data

    def nfsunmount(self, data):
        data = ProcModel.nfsunmount(data)
        return data

    def updatebiosdata(self, data):

        pass

    def templatedploy(self, data):
        data = ProcModel.templatedeploy(data)
        return data

    def checkbiosvalue(self, data):
        data = ProcModel.checkbiosvalue(data)
        return data

    def syscfgpatch(self, data):
        data = ProcModel.syscfgpatch(data)
        return data

    def dump(self, data):
        data = self.ipmicheck(data)
        data = self.ipmipowerstatus(data)
        data = self.reqiscsioff(data)
        data = self.syscfgdump(data)
        # data = self.nfsmount(data)
        data = self.biosdatacollect(data)
        # data = self.nfsunmount(data)
        # data = self.updatebiosdata(data)

    def set(self, data):
        data = self.ipmicheck(data)
        data = self.ipmipowerstatus(data)
        data = self.reqiscsioff(data)
        data = self.syscfgpatch(data)
        data = self.nfsmount(data)
        data = self.templatedploy(data)
        data = self.checkbiosvalue(data)
        data = self.biosdatacollect(data)
        data = self.nfsunmount(data)
        data = self.updatebiosdata(data)
        logger.info("====================== DATA ===================")
        logger.info("{}".format(data))


if __name__=="__main__":
    data = {}
    data['templatedata'] = bios_test()


