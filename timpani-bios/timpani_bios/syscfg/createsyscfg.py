import re
import copy
import datetime
import logging.handlers
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

class CreateSysCfg(object):

    def getNowStr(self, kind):
        now = datetime.datetime.now()
        nowDate = now.strftime('%Y%m%d%H%M%S')
        day = nowDate[:8]
        time = nowDate[8:]
        backupname = kind+'_'+nowDate
        getini_filename = 'getini_syscfg' + "_" + backupname + ".INI"
        redfish_filename = 'syscfg' + "_" + backupname + ".INI"
        return getini_filename, redfish_filename, backupname

    def create_template_syscfg(self, template_name, save_path, mount_path, orig_path, replace_list):

        getini_filename, redfish_filename, backupname = self.getNowStr(template_name)
        new_syscfg = save_path + "/" + getini_filename
        target_path = mount_path + new_syscfg
        new_fd = open(target_path, 'w')
        orig_fd = open(orig_path, 'r')

        while True:
            issave = True
            line = orig_fd.readline()
            if not line:
                break

            tmp_line = copy.deepcopy(line)
            for re_data in replace_list:
                syscfg_key = re_data.get('syscfg_key')
                pattern = re.compile(self.cleanText(syscfg_key))
                if pattern.search(self.cleanText(tmp_line)):
                    new_fd.write(re_data.get('set_line') + '\n')
                    issave = False
                    break
            if issave:
                new_fd.write(line)

        orig_fd.close()
        new_fd.close()

        return getini_filename, redfish_filename, backupname, target_path

    def get_version(self, save_path):
        BIOS_KEY = "BIOSVersion"
        FW_KEY = "FWOpcodeVersion"

        fd = open(save_path, 'r')
        bios_version = None
        fw_version = None
        while True:
            line = fd.readline()
            if not line:
                break

            if BIOS_KEY in line:
                bios_version = line.split('=')[1].split(' ')
            if FW_KEY in line:
                fw_version = line.split('=')[1].split(' ')

            if bios_version is not None and fw_version is not None:
                break

        fd.close()
        return bios_version, fw_version


    def vaild_setting_data_syscfgmove(self, src_path, target_path, replace_list):

        new_fd = open(target_path, 'w')
        orig_fd = open(src_path, 'r')

        if replace_list is None:
            replace_list = []
        valid_cnt = len(replace_list)
        match_cnt = 0
        while True:
            line = orig_fd.readline()
            if not line:
                break
            new_fd.write(line)

            for re_data in replace_list:
                redfish_key = re_data.get('redfish_key')
                redfish_val = re_data.get('redfish_val')
                pattern = re.compile(redfish_key)
                if pattern.search(line):
                    logger.info("match_line : {}".format(line))
                    match_words = line.split('=')
                    match_val = match_words[1].strip()
                    logger.info("match_val : {}, redfish_val : {}".format(match_val, redfish_val))
                    if match_val[0].__eq__(redfish_val):
                        logger.info("match count add")
                        match_cnt += 1
                    break

        orig_fd.close()
        new_fd.close()
        logger.info("match_cnt : {}, valid_cnt : {}".format(match_cnt, valid_cnt))
        if match_cnt == valid_cnt:
            isvalid = True
        else:
            isvalid = False

        return isvalid


    def replace_template_data(self, template_name, match_kind, template_data, match_data):
        replace_list = []
        for TData in template_data:
            name = TData.get('name')
            if name.__eq__(template_name):
                Tk = TData.get('redfish_key')
                Tv = TData.get('redfish_val')
                Ts = TData.get('cfg_set_val')
                for m in match_data:
                    kind = m.get('match_kind')
                    if kind.__eq__(match_kind):
                        syscfg_key = m.get('syscfg_key')
                        k = m.get('redfish_key')
                        if k.__eq__(Tk):
                            set_line = syscfg_key + "=" + Ts
                            save_data = {'syscfg_key':syscfg_key, 'syscfg_val': Ts, 'redfish_key': Tk,
                                         'redfish_val':Tv, 'set_line':set_line}
                            replace_list.append(save_data)
                            break
        return replace_list

    def cleanText(self, readData):
        res = re.sub('[-=+,#/\?:^\"\(\)\[\]\<\>\']','',readData)
        return res

    def movecfg(self, src_path, target_path, match_data, avail_data, template_data, guid, macaddr):
        BIOS_KEY = "BIOSVersion"
        FW_KEY = "FWOpcodeVersion"

        logger.info("[movecfg] src_path : {}".format(src_path))
        logger.info("[movecfg] terget_path : {}".format(target_path))
        targetfd = open(target_path, 'w')
        srcfd = open(src_path, 'r')

        bios_version = None
        fw_version = None

        match_kind_list = {}
        match_check_list = []
        match_check_data = {}

        match_check_cnt = 0
        unknow_list = []
        for tmp in match_data:
            mkind = tmp.get('match_kind')
            if mkind.__eq__('Default'):
                match_check_cnt += 1
                redfish_key = tmp.get('redfish_key')
                syscfg_key = tmp.get('syscfg_key')
                unknow_data = {'name': None,
                               'match_kind':'Unknow',
                               'redfish_key':redfish_key,
                               'syscfg_key':syscfg_key,
                               'cfg_set_val': 'Unknow',
                               'redfish_val': -1,
                               'cfg_bios_ver': None,
                               'cfg_fw_opcode': None,
                               'guid': guid,
                               'macaddr': macaddr
                               }
                unknow_list.append(unknow_data)

        while True:
            line = srcfd.readline()
            if not line:
                break

            targetfd.write(line)

            if BIOS_KEY in line:
                bios_version = line.split('=')[1].split(' ')[0]
            if FW_KEY in line:
                fw_version = line.split('=')[1].split(' ')[0]

            for match in match_data:
                matchkind = match.get('match_kind')
                redfish_key = match.get('redfish_key')
                matchkey = match.get('syscfg_key').replace(' ', '-').strip()
                sp_line = line.split('=')
                compare_word = sp_line[0].replace(' ', '-').strip()
                syscfg_key = sp_line[0].strip()
                cfg_set_val = None
                if len(sp_line) > 1:
                    cfg_set_val = sp_line[1].strip()
                    if ';' in cfg_set_val:
                        cfg_set_val = cfg_set_val.split(';')[0].strip()
                if re.match(self.cleanText(matchkey), self.cleanText(compare_word)):
                    isadd = True
                    for kind in match_check_list:
                        if matchkind.__eq__(kind):
                            isadd = False

                    if isadd:
                        match_check_list.append(matchkind)
                        match_check_data[matchkind] = 0
                        match_kind_list[matchkind] = []
                    match_check_data[matchkind] += 1
                    save_data = {'redfish_key': redfish_key, 'syscfg_key': syscfg_key, 'cfg_set_val': cfg_set_val}
                    match_kind_list[matchkind].append(save_data)

        targetfd.close()
        srcfd.close()

        logger.info("match_kind_list : {}".format(match_kind_list))
        match_kind = None
        for mkind in match_check_list:
            if match_check_data[mkind] == match_check_cnt:
                match_kind = mkind

        if match_kind is None:
            for tmp in unknow_list:
                tmp['cfg_bios_ver'] = bios_version
                tmp['cfg_fw_ver'] = fw_version
            return unknow_list

        template_match_list = []
        template_match_cnt = {}
        for tmp in match_kind_list[match_kind]:
            tmp['name'] = None
            redfish_key = tmp.get('redfish_key')
            cfg_set_val = tmp.get('cfg_set_val')

            for valdata in template_data:
                k = valdata.get('redfish_key')
                v = valdata.get('cfg_set_val')
                s = valdata.get('name')
                if redfish_key.__eq__(k):
                    if cfg_set_val.__eq__(v):
                        isadd = True
                        for t in template_match_list:
                            if s.__eq__(t):
                                isadd = False

                        if isadd:
                            template_match_list.append(s)
                            template_match_cnt[s] = 0
                        template_match_cnt[s] += 1

        template_name = None
        logger.info("template_match_list : {}".format(template_match_list))
        logger.info("template_match_cnt : {}".format(template_match_cnt))
        logger.info("match_check_cnt : {}".format(match_check_cnt))
        logger.info("match_kind_list : {}".format(match_check_cnt))
        for name in template_match_list:
            if template_match_cnt[name] == match_check_cnt:
                template_name = name

        for tmp in match_kind_list[match_kind]:
            tmp['cfg_bios_ver'] = bios_version
            tmp['cfg_fw_opcode'] = fw_version
            tmp['redfish_val'] = None
            tmp['name'] = template_name
            tmp['guid'] = guid
            tmp['macaddr'] = macaddr
            tmp['match_kind'] = match_kind
            redfish_key = tmp.get('redfish_key')
            cfg_set_val = tmp.get('cfg_set_val')
            for valdata in avail_data:
                k = valdata.get('redfish_key')
                v = valdata.get('cfg_set_val')
                s = valdata.get('redfish_val')
                if redfish_key.__eq__(k):
                    if cfg_set_val.__eq__(v):
                        tmp['redfish_val'] = s
        logger.info("template_name : {}".format(template_name))
        return match_kind_list[match_kind], template_name
