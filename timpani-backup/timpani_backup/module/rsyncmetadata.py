import logging
import re
import subprocess
from ..zfs import ZFS

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
stream_hander.setLevel(level=logging.INFO)
logger.addHandler(stream_hander)

class RsyncMetaData(object):

    def shell_run(self,shell_cmd):

        try:
            process = subprocess.Popen(shell_cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            returncode = process.wait()
        except subprocess.CalledProcessError as e:
            raise e

        return process.stdout.read()

    def getexclude(self, data):
        logger.info("data : {}".format(data))
        prefix_data = data.get('configdata').get('prefix')
        prefix = prefix_data.replace('/','')
        excludelist = []

        cmd = "ls -al / | awk '{print $1, $9}'"
        output = self.shell_run(cmd)
        sp_out = output.split('\n')
        for raw_data in sp_out:
            word = raw_data.split(' ')
            pattern = re.compile('d')
            if pattern.search(word[0]):
                exclude_pattern = re.compile(prefix)
                if exclude_pattern.search(word[1]):
                    if len(prefix) < len(word[1]):
                        if '-' in word[1]:
                            excludelist.append('/'+word[1]+'/*')
                    else:
                        excludelist.append('/'+word[1]+'/*')

        return excludelist

    def linuxdatadir(self, prefix_data, uuid, modulename):
        prefix = prefix_data.replace('/','')
        datalist = []
        uuid_s = uuid.replace('-','').upper()
        cmd = "ls -al / | awk '{print $1, $9}'"
        output = self.shell_run(cmd)
        sp_out = output.split('\n')
        for raw_data in sp_out:
            word = raw_data.split(' ')
            pattern = re.compile('d')
            if pattern.search(word[0]):
                exclude_pattern = re.compile(prefix)
                if exclude_pattern.search(word[1]):
                    if len(prefix) < len(word[1]):
                        if '-' in word[1]:
                            dirname = '/'+ word[1]
                            save_data = {'usetype': 'data', 'name': dirname, 'uuid': uuid_s, 'modulename': modulename, 'nodetype':'MASTER'}
                            datalist.append(save_data)
                    else:
                        dirname = '/'+word[1]
                        save_data = {'usetype': 'data', 'name': dirname, 'uuid': uuid_s, 'modulename': modulename,
                                     'nodetype': 'MASTER'}
                        datalist.append(save_data)

        return datalist

    def freebsddatadir(self, prefix_data, uuid, modulename):
        prefix = prefix_data.replace('/','')
        excludelist = []
        uuid_s = uuid.replace('-', '').upper()
        cmd = "zpool list -H | awk '{print $1}'"
        output = self.shell_run(cmd)
        sp_out = output.split('\n')
        checkpools = []
        for raw_data in sp_out:
            if len(raw_data) > 1:
                pattern = re.compile(prefix)
                if pattern.search(raw_data):
                    save_data = {'usetype': 'data', 'name': raw_data, 'uuid': uuid_s, 'modulename':modulename, 'nodetype': 'STORAGE'}
                    checkpools.append(save_data)
                else:
                    save_data = {'usetype': 'os', 'name': raw_data, 'uuid': uuid_s, 'modulename':modulename, 'nodetype': 'STORAGE'}
                    checkpools.append(save_data)

        return checkpools

    def collect_disk_dev(self):
        devicelist = []
        bootdevname = None

        try:
            stdout = ZFS.dev_list_linux()
            line = stdout.split('\n')
            logger.info('devicelist stdout : {}'.format(line))
            for raw in line:
                value = raw.strip()
                if not value.__eq__(''):
                    devicelist.append(value)
        except Exception as e:
            logger.info("Exception Collect Disk Device : {}".format(e))
        logger.info('devicelist : {}'.format(devicelist))

        for devname in devicelist:
            try:
                dev_path = "/dev/{}".format(devname)
                stdout = ZFS.dev_boot_linux(dev_path)
                line = stdout.split('/n')
                tmp_devname = None
                for raw in line:
                    tmp = raw.split(' ')
                    if not tmp[0].__eq__(''):
                        tmp_devname = tmp[0]

                    if tmp_devname is not None:
                        if bootdevname is None:
                            bootdevname = tmp_devname
                        else:
                            bootdevname += ','+tmp_devname
            except Exception as e:
                logger.info("Exception Find Boot Device : {}".format(e))
            logger.info('bootdevname : {}'.format(bootdevname))
        return {'pool':None, 'path':None, 'devname':bootdevname}, devicelist

    def matadatacollect(self, data):
        data['exclude_list'] = self.getexclude(data)
        bootdata, devicelist = self.collect_disk_dev()
        data['bootdata'] = bootdata
        data['devicelist'] = devicelist
        return data


