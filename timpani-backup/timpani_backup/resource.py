import re
import os
import platform
import subprocess
import distro
import logging
from timpani_backup.zfs import ZFS

logger = logging.getLogger(__name__)

class ResourceSystem(object):

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

        # logger.debug("result : {}".format(result_data))
        return result_data

    @staticmethod
    def getZfsGetAll():
        try:
            output = ZFS.zfs_get(zfs_types=['filesystem','volume'])
        except RuntimeError:
            logger.info("Exception RUN Error")

        # logger.debug("output : {}".format(output))
        sp_output = output.split('\n')
        ZFS_RESULT_TEMPLETE = {'dataset': None, 'property': None, 'value': None, 'source': None}
        # logger.debug("sp_output : {}".format(sp_output))
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
            
        # logger.debug("snapshot list : {}".format(output))
        sp_output = output.split('\n')
        result_data = []
        dataset_list = []
        dataset_snapname = []
        for raw in sp_output:
            values = raw.split('\t')
            if len(values) > 1:
                result_data.append(values[0])
                dataset_val = values[0].split('@')
                dataset_list.append(dataset_val[0])
                dataset_snapname.append(dataset_val[1])

        return result_data, dataset_list, dataset_snapname

    @staticmethod
    def getSnapShotSaveList(target):
        try:
            output = ZFS.zfs_get(target=target, recursive=True, zfs_types=['snapshot'], parsable=True, properties=['creation'])
            logger.info("snapshot save list : {}".format(output))
        except RuntimeError:
            logger.info("Exception RUN Error")

        sp_output = output.split('\n')
        result_data = []
        dataset_list = []
        dataset_snapname = []
        for raw in sp_output:
            values = raw.split('\t')
            if len(values) > 1:
                dataset_name = values[0].split('@')[0]
                snapname = values[0].split('@')[1]
                snapshot_name = values[0]
                snapshot_createtime = values[2]
                result_data.append((target, dataset_name, snapname, snapshot_name, snapshot_createtime))

        return result_data


    @staticmethod
    def findfullbackup(dataset_name):
        try:
            output = ZFS.zfs_list(zfs_types=['snapshot'])
        except RuntimeError:
            logger.info("Exception RUN Error")

        # logger.debug("snapshot list : {}".format(output))
        sp_output = output.split('\n')
        find_result = None
        for raw in sp_output:
            values = raw.split('\t')
            if len(values) > 3:
                dataset_val = values[0].split('@')
                if dataset_val[0].__eq__(dataset_name):
                    if dataset_val[1].find('F-') is 0:
                        find_result = values[0]
                    else:
                        ResourceSystem.FullDestorySnapshot(values[0])

        return find_result

    @staticmethod
    def getZpoolList():
        try:
            output = ZFS.zpool_list()
            # print(output)
        except RuntimeError:
            logger.info("Exception RUN Error")

        # logger.debug("snapshot list : {}".format(output))
        sp_output = output.split('\n')
        result_data = []
        for raw in sp_output:
            values = raw.split('\t')
            if len(values) > 3:
                result_data.append(values[0])
        return result_data

    @staticmethod
    def getZfsList(target, recursive: bool = False, zfs_types: list = None):
        try:
            output = ZFS.zfs_list(target=target, recursive=recursive, zfs_types= zfs_types)
        except RuntimeError:
            logger.info("Exception RUN Error")

        # logger.debug("snapshot list : {}".format(output))
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
    def gpart_backup(device, target_host, remote_backup):
        try:
            output = ZFS.gpart_backup(device=device, target_host=target_host, remote_path=remote_backup)
        except:
            logger.info("Exception RUN Error")

        return output

    @staticmethod
    def zpoollistHv(realpath:bool=False):
        try:
            output = ZFS.zpool_list(verbose=True, realpath=realpath)
        except:
            logger.info("Exception RUN Error")

        sp_output = output.split('\n')
        logger.debug(sp_output)
        pool_cnt = 0
        raid_cnt = 0
        mirror_cnt = 0
        res_data = []
        pool_data = None

        for raw_data in sp_output:
            data = raw_data.split('\t')
            if data[0] is not '' and len(data) > 1:
                pool = data[0]
                pool_cnt += 1
                if pool_data is None:
                    pool_data = {}
                else:
                    res_data.append(pool_data)
                    pool_data = {}
                pool_data['pool'] = pool

            if pool_cnt > 0 and len(data) > 1:
                if (data[0] is '') and (data[1] is not ''):
                    if data[1].find('raidz') > -1 or data[1].find('mirror') > -1:
                        raid_kind_data = data[1].split('-')
                        raid_kind = raid_kind_data[0]
                        if len(raid_kind_data) > 1:
                            raid_create_cnt = raid_kind_data[1]
                        else:
                            raid_create_cnt = '0'
                        pool_data['raid'] = {'method': raid_kind,'create_cnt': raid_create_cnt, 'device_list': []}
                    else:
                        disk = data[1]
                        if 'raid' in pool_data:
                            pool_data['raid']['device_list'].append(disk)
                        else:
                            pool_data['raid'] = {'method': 'stripe', 'create_cnt': '0', 'device_list': []}
                            pool_data['raid']['device_list'].append(disk)

        res_data.append(pool_data)
        # print(res_data)
        return res_data

    @staticmethod
    def geomlist():
        try:
            output = ZFS.geom_list()
        except:
            logger.info("Exception RUN Error")

        sp_output = output.split('\n')
        result_size = len(sp_output)
        result_list = []
        geom_data = {}
        is_save = True
        for raw in sp_output:
            data = raw.split(':')
            if len(data) > 1:
                k = data[0].strip()
                v = data[1].strip()
                if 'Name' in k:
                    k = 'Name'
                    if 'cd' in v:
                        is_save = False
                if 'Mediasize' in k:
                    v = v[:v.find('(')].strip()
                geom_data[k.lower().replace(' ','_')] = v
                # print("key : {}, value: {}".format(k,v))
            else:
                if is_save:
                    if len(geom_data) > 0:
                        result_list.append(geom_data)
                geom_data = {}
                is_save = True

        logger.debug(result_list)
        return result_list

    @staticmethod
    def zdb_list():
        try:
            output = ZFS.zdb_list()
            logger.debug(output)
        except:
            logger.info("Exception RUN Error")
        sp_output = output.split('\n')
        result_size = len(sp_output)
        # print(sp_output)
        res_data = []
        pool_info = None
        children_cnt = -1
        children_data = None
        sub_cnt=0
        for raw_data in sp_output:
            data = raw_data.split(':')
            if len(data) > 1:
                k = data[0]
                v = data[1]
            else:
                continue

            if k[:1].__eq__(' '):
                #4,8,12,16
                # print(k)
                if k[15:16].__eq__(' '):
                    sub_cnt = 4
                elif k[11:12].__eq__(' '):
                    sub_cnt = 3
                elif k[7:8].__eq__(' '):
                    sub_cnt = 2
                elif k[3:4].__eq__(' '):
                    sub_cnt = 1

                # print(sub_cnt)
                if sub_cnt is 1:
                    if k.find('vdev_tree') > 0:
                        pool_info['pool_info']['vdev_tree'] = {}
                    elif k.find('features_for_read') > 0:
                        if children_data is not None:
                            if children_data_sub is not None:
                                children_data['children_sub'].append(children_data_sub)
                            pool_info['pool_info']['vdev_tree']['children'].append(children_data)
                        pool_info['pool_info']['features_for_read'] = {}
                    else:
                        pool_info['pool_info'][k.strip(' ')] = v.replace("'", '').strip(' ')

                elif sub_cnt is 2:
                    if k.find('children') > 0:
                        if not 'children' in pool_info['pool_info']['vdev_tree']:
                            pool_info['pool_info']['vdev_tree']['children'] = []
                        if children_data is not None:
                            pool_info['pool_info']['vdev_tree']['children'].append(children_data)
                        children_cnt += 1
                        children_data = None
                        children_data_sub = None
                    else:
                        if 'features_for_read' in pool_info['pool_info']:
                            pool_info['pool_info']['features_for_read'][k.strip(' ')] = v.replace("'",'').strip(' ')
                        else:
                            pool_info['pool_info']['vdev_tree'][k.strip(' ')] = v.replace("'",'').strip(' ')
                elif sub_cnt is 3:
                    if k.find('children') > 0:
                        if not 'children_sub' in children_data:
                            children_data['children_sub'] = []
                        if children_data_sub is not None:
                            children_data['children_sub'].append(children_data_sub)
                        children_data_sub = None
                    else:
                        if children_data is None:
                            children_data = {}
                        children_data[k.strip(' ')] = v.replace("'",'').strip(' ')
                elif sub_cnt is 4:
                    if children_data_sub is None:
                        children_data_sub = {}
                    children_data_sub[k.strip(' ')] = v.replace("'",'').strip(' ')
            else:
                if pool_info is not None:
                    res_data.append(pool_info)
                pool_info = {'pool':k , 'pool_info':{}}
                sub_cnt = 0


        if pool_info is not None:
            if len(pool_info) > 0:
                res_data.append(pool_info)
        # print(res_data)
        return res_data

    @staticmethod
    def zpoolStatus():
        try:
            output = ZFS.zpool_status()
        except:
            logger.info("Exception RUN Error")

        # print("zpoolStatus : {}".format(output))
        sp_output = output.split('\n')
        result_size = len(sp_output)
        result_list = []
        # print(sp_output)
        for i in range(0, int(result_size/10)):
            print(i)
            if (result_size >= i*10) and (result_size < (i+1)*10):
                templte = {'pool_name': sp_output[i*10 + 1].replace('\n', ''), 'status': sp_output[i*10 + 3].replace('\n', ''),
                           'scan' : sp_output[i*10 + 5].replace('\n', ''),
                           'config' : sp_output[i*10 + 7].replace('\n', ''), 'error': sp_output[i*10 + 9].replace('\n', '')
                        }
                result_list.append(templte)

        # print("result_list : ".format(result_list))


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
            result = ZFS.zfs_snapshot(filesystem=poolname, snapname=snapname, recursive=True)
            result_list, _, _ = ResourceSystem.getSnapShotList()
            return result_list

        except RuntimeError:
            logger.info("Exception Run Error")

    @staticmethod
    def IncrementSnapshot(dataset:str, snapname: str):
        try:
            result = ZFS.zfs_snapshot(filesystem=dataset, snapname=snapname, recursive=True)
            # logger.info("Increment snapshot : {}".format(result))
            result_list, _, _ = ResourceSystem.getSnapShotList()
            # logger.info("AFTER snapshot list : {}".format(result_list))
            return result_list

        except RuntimeError:
            logger.info("Exception Run Error")

    @staticmethod
    def Snapshot(dataset: str, snapname: str, recursive: bool):
        try:
            snap_full_name = "{}@{}".format(dataset, snapname)
            ZFS.zfs_snapshot(filesystem=dataset, snapname=snapname, recursive=recursive)
            snap_info = ResourceSystem.getSnapShotSaveList(snap_full_name)
            return snap_info

        except RuntimeError:
            logger.info("Exception Run Error")
            return None

    @staticmethod
    def DestorySnapshot(snapname):
        try:
            ZFS.zfs_destroy_snapshot(snapname=snapname)
            return True
        except RuntimeError:
            logger.info("Exception Run Error")
            return False

    @staticmethod
    def IncrementBackupSend(send_target: str, parent_target: str, target_host: str, remote_path: str):
        try:
            # if parent_target is None:
            #     result = ZFS.zfs_send(send_target=send_target, parent_target=None, target_host=target_host, isfull=True,
            #                       remote_path=remote_path)
            # else:
            result = ZFS.zfs_send(send_target=send_target, parent_target=parent_target, target_host=target_host, isfull=False,
                                remote_path=remote_path)
            return result
        except RuntimeError:
            logger.info("Exception Run Error")

    @staticmethod
    def IncrementDestorySnapshot(snapname):
        try:
            result_data, _, _ = ResourceSystem.getSnapShotList()
            # logger.info("PRE snapshot list : {}".format(result_data))
            output = ZFS.zfs_destroy_snapshot(snapname=snapname)
            result_data, _, _ = ResourceSystem.getSnapShotList()
            # logger.info("AFTER snapshot list : {}".format(result_data))
        except RuntimeError:
            logger.info("Exception Run Error")


    # @staticmethod
    # def FullSnapshot(poolname: str, snapname: str):
    #     try:
    #         result = ZFS.zfs_snapshot(filesystem=poolname, snapname=snapname, recursive=False)
    #         # logger.info("FULL snapshot : {}".format(result))
    #         result_list, _, _ = ResourceSystem.getSnapShotList()
    #         # logger.info("AFTER snapshot list : {}".format(result_list))
    #         return result_list
    #
    #     except RuntimeError:
    #         logger.info("Exception Run Error")

    @staticmethod
    def FullBackupSend(send_target: str, target_host: str, remote_path: str):
        try:
            result = ZFS.zfs_send(send_target=send_target, parent_target=None, target_host=target_host, isfull=True, remote_path=remote_path)
            return result
        except RuntimeError:
            logger.info("Exception Run Error")


    @staticmethod
    def FullDestorySnapshot(snapname):
        try:
            result_data, _, _ = ResourceSystem.getSnapShotList()
            # logger.info("PRE snapshot list : {}".format(result_data))
            output = ZFS.zfs_destroy_snapshot(snapname=snapname)
            result_data, _, _ = ResourceSystem.getSnapShotList()
            # logger.info("AFTER snapshot list : {}".format(result_data))
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

