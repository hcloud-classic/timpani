import re
import os
import platform
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
            return {'os_type': sysname, 'os_version': os_release, 'os_name': sysname, 'os_arch': os_arch,
                    'kernel_version': None, 'hostname': nodename}

    @staticmethod
    def getSystemZfsList():
        try:
            output = ZFS.zfs_list(target=None, zfs_types=["filesystem"])
        except RuntimeError:
            logger.info("Exception RUN ERROR")

        sp_output = output.split()
        logger.info(sp_output)
        ZFSLIST_HEADER_LIST = ["zfs_name", "zfs_used_size", "zfs_avail_size", "zfs_ref_size", "zfs_mount_point"]

        i = 0
        res = []
        for raw in sp_output:
            if i == 0:
                line = {}
            line[ZFSLIST_HEADER_LIST[i]] = raw
            # logger.debug("{} : {}".format(line, raw))
            if ZFSLIST_HEADER_LIST[i].__eq__("zfs_mount_point"):
                if not raw.__eq__('-'):
                    logger.debug(ResourceSystem.getSystemDiskFree(raw))
            i += 1
            i %= 5

            if i == 0:
                res.append(line)

        result = {"zfs_list": res}
        return result

    @staticmethod
    def getZpoolGetAll():
        try:
            output = ZFS.zpool_get()
        except RuntimeError:
            logger.info("Exception RUN Error")

        # logger.info("output : {}".format(output))
        sp_output = output.split('\n')
        ZPOOL_RESULT_TEMPLETE = {'dataset': None, 'property': None, 'value': None, 'source': None}
        logger.debug("sp_output : {}".format(sp_output))
        result_data = []
        for raw in sp_output:
            values = raw.split('\t')
            if len(values) == 4:
                dataset = values[0]
                property = values[1] if not values[1].__eq__('-') else None
                property_value = values[2] if not values[2].__eq__('-') else None
                property_source = values[3] if not values[3].__eq__('-') else None
                result_data.append({'dataset': dataset,
                                'property': property,
                                'value': property_value,
                                'source': property_source})

        logger.debug("result : {}".format(result_data))
        return result_data

    @staticmethod
    def getZfsGetAll():
        try:
            output = ZFS.zfs_get(zfs_types=['filesystem','volume'])
        except RuntimeError:
            logger.info("Exception RUN Error")

        logger.debug("output : {}".format(output))
        sp_output = output.split('\n')
        ZFS_RESULT_TEMPLETE = {'dataset': None, 'property': None, 'value': None, 'source': None}
        logger.debug("sp_output : {}".format(sp_output))
        result_data = []
        for raw in sp_output:
            values = raw.split('\t')
            if len(values) == 4:
                dataset = values[0]
                property = values[1] if not values[1].__eq__('-') else None
                property_value = values[2] if not values[2].__eq__('-') else None
                property_source = values[3] if not values[3].__eq__('-') else None
                result_data.append({'dataset': dataset,
                                    'property': property,
                                    'value': property_value,
                                    'source': property_source})

        logger.debug("result : {}".format(result_data))
        return result_data

    @staticmethod
    def getSnapShotList():
        try:
            output = ZFS.zfs_list(zfs_types=['snapshot'])
        except RuntimeError:
            logger.info("Exception RUN Error")
            
        logger.debug("snapshot list : {}".format(output))
        sp_output = output.split('\n')
        result_data = []
        dataset_list = []
        dataset_snapname = []
        for raw in sp_output:
            values = raw.split('\t')
            if len(values) > 3:
                result_data.append(values[0])
                dataset_val = values[0].split('@')
                dataset_list.append(dataset_val[0])
                dataset_snapname.append(dataset_val[1])

        return result_data, dataset_list, dataset_snapname

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
                result_data.append((values[0], mount_point))
        return result_data

    @staticmethod
    def gpart_backup():
        try:
            output = ZFS.gpart_backup()
        except:
            logger.info("Exception RUN Error")
        sp_output = output.split('\n')
        result_data = []
        for raw in sp_output:
            values = raw.strip().split(' ')
            if len(values) > 1:
                if platform.system() == "FreeBSD":
                    result_data.append((values[3], values[1].replace('(', '').replace(')', '')))
                else:
                    result_data.append((values[0], values[2]))

        return result_data

    @staticmethod
    def zpoolStatus():
        try:
            output = ZFS.zpool_status()
        except:
            logger.info("Exception RUN Error")

        print("zpoolStatus : {}".format(output))
        sp_output = output.split('\n')
        result_size = len(sp_output)
        result_list = []
        print(sp_output)
        for i in range(0, int(result_size/10)):
            print(i)
            if (result_size >= i*10) and (result_size < (i+1)*10):
                templte = {'pool_name': sp_output[i*10 + 1].replace('\n', ''), 'status': sp_output[i*10 + 3].replace('\n', ''),
                           'scan' : sp_output[i*10 + 5].replace('\n', ''),
                           'config' : sp_output[i*10 + 7].replace('\n', ''), 'error': sp_output[i*10 + 9].replace('\n', '')
                        }
                result_list.append(templte)

        print("result_list : ".format(result_list))


        result_data = []
        # for raw in sp_output:
        #     print("zpoolStatus raw : {}".format(raw))
        #     values = raw.strip().split(' ')

            # if len(values) > 1:
            #     if platform.system() == "FreeBSD":
            #         result_data.append((values[3], values[1].replace('(', '').replace(')', '')))
            #     else:
            #         result_data.append((values[0], values[2]))

        return result_data

    @staticmethod
    def timpani_checksum(dataset:str, mountpoint:str):
        if mountpoint is None:
            return []
        output = ''
        try:
            output = ZFS.timpani_checksum_testfile_create(dataset=dataset)
            # print("timpani_checksum : {}".format(output))
        except RuntimeError:
            logger.info("Exception RUN Error")

        sp_output = output.split('\n')
        result_data = []
        for raw in sp_output:
            values = raw.strip().split(' ')
            if len(values) > 1:
                if platform.system() == "FreeBSD":
                    result_data.append((values[3], values[1].replace('(', '').replace(')', '')))
                else:
                    result_data.append((values[0], values[2]))

        return result_data

    @staticmethod
    def FullSnapshot(poolname:str, snapname:str):
        try:
            result = ZFS.zfs_snapshot(filesystem=poolname, snapname=snapname, recursive=False)
            logger.info("FULL snapshot : {}".format(result))
            result_list, _, _ = ResourceSystem.getSnapShotList()
            logger.info("AFTER snapshot list : {}".format(result_list))
            return result_list

        except RuntimeError:
            logger.info("Exception Run Error")

    @staticmethod
    def FullBackupSend(send_target: str, target_host: str, remote_path: str):
        try:
            result = ZFS.zfs_send(send_target=send_target, target_host=target_host, isfull=True, remote_path=remote_path)
            return result
        except RuntimeError:
            logger.info("Exception Run Error")


    @staticmethod
    def FullDestorySnapshot(snapname):
        try:
            result_data, _, _ = ResourceSystem.getSnapShotList()
            logger.info("PRE snapshot list : {}".format(result_data))
            output = ZFS.zfs_destroy_snapshot(snapname=snapname)
            result_data, _, _ = ResourceSystem.getSnapShotList()
            logger.info("AFTER snapshot list : {}".format(result_data))
        except RuntimeError:
            logger.info("Exception Run Error")


    @staticmethod
    def getSystemDiskFree(mount_path):
        # LINUX
        st = os.statvfs(mount_path)
        free = st.f_bavail * st.f_frsize
        total = st.f_blocks * st.f_frsize
        used = (st.f_blocks - st.f_bfree) * st.f_frsize

        return mount_path, free, total, used

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

