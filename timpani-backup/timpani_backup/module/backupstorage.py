import logging
import re
import copy
from ..zfs import ZFS
from ..util.systemutil import Systemutil

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
stream_hander.setLevel(level=logging.INFO)
logger.addHandler(stream_hander)

class BackupStorage(object):

    systemutil = Systemutil()

    def mount_parser(self, sp_output, nfs_server):
        devicelist=[]
        isbackupstoragemount = False
        # logger.info("====================== [ MOUNT ] =========================")
        for raw in sp_output:
            # logger.info("raw : {}".format(raw))
            sp_data = raw.split(' ')
            comp_str = "\/dev"
            pattern = re.compile(comp_str)
            if pattern.search(sp_data[0]):
                # logger.info("DEVICE : {}".format(sp_data[0]))
                devicelist.append({'device':sp_data[0], 'mountpath':sp_data[1]})

            pattern =re.compile(nfs_server)
            if pattern.search(sp_data[0]):
                # logger.info("nfsmount : True")
                isbackupstoragemount = True

        # logger.info("\n")
        return devicelist, isbackupstoragemount

    def collect_check_mount(self, nfs_server):
        try:
            stdout = ZFS.mount_grep(None)
            line =stdout.split('\n')
            devicelist, isnfsmount = self.mount_parser(line, nfs_server)
        except Exception as e:
            logger.info("[searchvolumedataset] EXCEPT : {}".format(e))

        return devicelist, isnfsmount

    def mount_exec(self, source, target):
        try:
            logger.info("mount target : {}, source : {}".format(target, source))
            stdout = ZFS.nfsmount(source, target)
            logger.info("mount stdout : {}".format(stdout))
        except Exception as e:
            logger.info("[mount_exec] EXCEPT : {}".format(e))

    def unmount_exec(self, target):
        try:
            stdout = ZFS.nfsunmount(target)
        except Exception as e:
            logger.info("[mount_exec] EXCEPT : {}".format(e))

    def nfsmount(self, nfs_server, export_path, mount_path):
        devicelist, isnfsmount = self.collect_check_mount(nfs_server)
        if not isnfsmount:
            target_path = nfs_server+":"+export_path
            self.systemutil.dirExistCheckAndCreate(mount_path)
            self.mount_exec(target_path, mount_path)
        _, isnfsmount = self.collect_check_mount(nfs_server)

        if isnfsmount:
            logger.info("NFS MOUNT SUCCESS")
        else:
            logger.info("NFS MOUNT FAILED")
        return devicelist, isnfsmount

    def nfsunmount(self, nfs_server, export_path, mount_path):
        devicelist, isnfsmount = self.collect_check_mount(nfs_server)
        if isnfsmount:
            self.unmount_exec(mount_path)
        _, isnfsmount = self.collect_check_mount(nfs_server)
        self.systemutil.dirExistCheckAndDelete(mount_path)
        if not isnfsmount:
            logger.info("NFS UNMOUNT SUCCESS")
        else:
            logger.info("NFS UNMOUNT FAILED")
        return isnfsmount




