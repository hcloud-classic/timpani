import re
import os
import json
import platform
import psutil
import subprocess
import distro
import logging
from timpani_system.zfs import ZFS

logger = logging.getLogger(__name__)

class ResourceSystem(object):

    @staticmethod
    def getBaseInformation():
        #sysname = 'Linux', nodename = 'localhost', release = '4.15.0-120-generic'

        uname_res = os.uname()
        sysname = uname_res.sysname
        nodename = uname_res.nodename
        os_arch = uname_res.machine
        if sysname.__eq__('Linux'):
            kernel_release = uname_res.release
            ret = subprocess.check_output('grep PRETTY_NAME /etc/*-release', shell=True)
            ret_str = ret.decode('utf-8')
            os_name_str = ret_str.split('=')[1].replace('"','').replace('\n','')
            os_strs = os_name_str.split(' ')
            if os_strs[0].__eq__('CentOS'):
                os_name = os_strs[0]
                os_version = os_strs[2]
            elif os_strs[0].__eq__('Ubuntu'):
                os_name = os_strs[0]
                os_version = os_strs[1]
            return {'os_type': sysname, 'os_version': os_version, 'os_name': os_name, 'os_arch':os_arch, 'kernel_version': kernel_release, 'hostname': nodename}
        elif sysname.__eq__('FreeBSD'):
            os_release = uname_res.release
            return { 'os_type': sysname, 'os_version': os_release, 'os_name': sysname, 'os_arch': os_arch,
                    'kernel_version': None, 'hostname': nodename }

    @staticmethod
    def getSystemZfsList(target, zfs_type_list, res_list):
        try:
            output = ZFS.zfs_list(target=target, zfs_types=zfs_type_list, recursive=True)
        except RuntimeError:
            logger.info("Exception RUN ERROR")

        sp_output = output.split()
        logger.info(sp_output)
        ZFSLIST_HEADER_LIST = ["zfs_name", "zfs_used_size", "zfs_avail_size", "zfs_ref_size", "zfs_mount_point"]

        i = 0
        if res_list is None:
            res_list = []

        for raw in sp_output:
            if i == 0:
                line = {}
            line[ZFSLIST_HEADER_LIST[i]] = raw
            # logger.debug("{} : {}".format(line, raw))
            # if ZFSLIST_HEADER_LIST[i].__eq__("zfs_mount_point"):
            #     if not raw.__eq__('-'):
            #         logger.debug(ResourceSystem.getSystemDiskFree(raw))
            i += 1
            i %= 5

            if i == 0:
                line['zpool_name'] = target
                line['zfs_type'] = zfs_type_list[0]
                res_list.append(line)

        return res_list

    @staticmethod
    def getZpoolList():
        try:
            output = ZFS.zpool_list()
            # print(output)
        except RuntimeError:
            logger.info("Exception RUN Error")

        logger.debug("snapshot list : {}".format(output))
        sp_output = output.split('\n')
        result_data = []
        for raw in sp_output:
            values = raw.split('\t')
            if len(values) > 3:
                result_data.append(values[0])
        return result_data

    @staticmethod
    def CheckZFS():
        try:
            output = ZFS.check_zfs()
        except RuntimeError:
            logger.info("Check ZFS Type Error")

        return output

    @staticmethod
    def CheckMountDirectory():
        try:
            output = ZFS.check_backup_target()
        except RuntimeError:
            logger.info("Check ZFS Type Error")
        logger.info("CHECKMOUNTDIRECTORY : {}".format(output))
        if output is not None:
            sp_output = output.split('\n')
            target = []
            for raw in sp_output:
                values = raw.split('{')
                if len(values) > 1:
                    temp = values[1].split('},')
                    if len(temp) > 0:
                        if len(temp[0]) > 0:
                            logger.info("test : {}".format(temp[0]))
                            dic_data = temp[0].split(',')
                            temp_dic = {}
                            for dic_value in dic_data:
                                t = dic_value.strip(' ').split(':')
                                logger.info('{} {}'.format(t[0], t[1]))
                                k = t[0].strip('"')
                                v = t[1].strip(' ').strip('"')
                                temp_dic[k] = v if not v.__eq__('null') else None
                                logger.info("dic_data : {}".format(temp_dic))

                            if temp_dic['fstype'] is not None:
                                target.append(temp_dic)
            logger.info("target : {}".format(target))
            return target

    @staticmethod
    def CheckUserHome():
        try:
            output = ZFS.check_user_home()
        except RuntimeError:
            logger.info("Check ZFS Type Error")

        dic_datas = json.loads(output, encoding='utf-8')
        dir_list = []
        for dir_data in dic_datas:

            if dir_data['type'].__eq__('directory') and dir_data['name'].__eq__('/home'):
                dir_list_data = dir_data['contents']
                for data in dir_list_data:
                    dir_name = "/home/{}".format(data['name'])
                    dir_list.append(dir_name)
        return dir_list

    @staticmethod
    def getZfsList(target, recursive: bool = False):
        try:
            output = ZFS.zfs_list(target=target, recursive=recursive)
        except RuntimeError:
            logger.info("Exception RUN Error")

        logger.debug("snapshot list : {}".format(output))
        sp_output = output.split('\n')
        result_data = []
        for raw in sp_output:
            values = raw.split('\t')
            if len(values) > 3:
                if values[4].__eq__('-') or values[4].__eq__('none'):
                    mount_point = None
                else:
                    mount_point = values[4]
                if mount_point is not None:
                    result_data.append((values[0], mount_point))
        return result_data

    @staticmethod
    def GetBackupSrcList(res_list):
        # Get ZPOOL Name List
        zfs_type = [['filesystem'], ['volume']]
        if res_list is None:
            res_list = []
        logger.info("GetBackupSrcList : {}".format(res_list))
        zpool_list = ResourceSystem.getZpoolList()
        for zpool_name in zpool_list:
            for zfs_type_list in zfs_type:
                ResourceSystem.getSystemZfsList(target=zpool_name, zfs_type_list=zfs_type_list, res_list=res_list)
        logger.info("GetBackupSrcList : {}".format(res_list))

        return res_list

    @staticmethod
    def getSystemDiskFree(mount_path):
        # LINUX
        used = psutil.disk_usage(mount_path).used
        free = psutil.disk_usage(mount_path).free
        # st = os.statvfs(mount_path)
        # free = st.f_bavail * st.f_frsize
        # total = st.f_blocks * st.f_frsize
        # used = (st.f_blocks - st.f_bfree) * st.f_frsize

        availe_v = ResourceSystem.div_value(free)
        used_v = ResourceSystem.div_value(used)

        return '-', used_v, availe_v, '-', mount_path

    @staticmethod
    def div_value(v):
        DIV = ' KMGT'
        div_float = 0.0
        div_v = 1000
        div_cnt = 0
        result = 0.0
        for d in DIV:
            div_float = v/div_v
            ret = round(div_float,2)
            # logger.info("float : {} {}".format(div_float, ret))
            if div_float < 1000:
                if div_v is 1000:
                    result = v
                else:
                    result = ret
                    div_cnt += 1
                break

            div_v *= 1024
            div_cnt += 1
        res_str = "{}{}".format(result, DIV[div_cnt:(div_cnt+1)])
        return res_str

    @staticmethod
    def getBaseSystemInfo():
        uname = os.uname()
        os_type = uname[0]
        hostname = uname[1]
        kernel_version = uname[2]
        arch = uname[4]
        os_name, os_version, _ = distro.linux_distribution()

        res = {'os_type': os_type, 'hostname': hostname, 'kernel_version': kernel_version, 'os_arch': arch,
               'os_name': os_name, 'os_version': os_version}
        return res

