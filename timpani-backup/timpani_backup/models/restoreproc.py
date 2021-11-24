import logging
from ..module.zvolmetadata import zvolMetaData
from ..module.backupstorage import BackupStorage
from ..module.snapshot import Snapshot
from ..module.iscsi import IscsiProc
from ..module.snapshotrestore import SnapshotRestore

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
stream_hander.setLevel(level=logging.INFO)
logger.addHandler(stream_hander)

class RestoreProc(object):

    def zvolmetadataget(self, data):
        return data

    def zvolmetadatacollect(self, data):
        dataset = data.get('name')
        meta = zvolMetaData(dataset, True)
        logger.info("zvol meta data collection")
        cur_collectdata = meta.collect_zfs()
        data['cur_collectdata'] = cur_collectdata
        return data


    def metadatacompare(self, data):
        return data

    def iscsidemoncheck(self, data):
        iscsi = IscsiProc()
        data['isiscsirun'] = iscsi.demoncheck()
        return data

    def iscsirequnmount(self, data):
        isiscsirun = data.get('isiscsirun')
        if isiscsirun:
            data['isrequmount'] = True
        return data

    def iscsireqmount(self, data):
        isrequmount = data.get('isrequmount')
        if isrequmount:
            data['isreqmount'] = True
        return data

    def iscsiluninfodel(self, data):
        iscsi = IscsiProc()
        data = iscsi.iscsilunremove(data)
        return data

    def iscsiluninfoadd(self, data):
        iscsi = IscsiProc()
        data = iscsi.iscsilunadd(data)
        return data

    def datasetrename(self, data):
        mount_path = data.get('mount_path')
        # full snapshot create
        snap = SnapshotRestore()
        snap.rollbacksnapshotcreate(data)
        return data

    def renamedatadel(self, data):
        snap = SnapshotRestore()
        snap.rollbacksnapshotdestroy(data)
        return data

    def rollback(self, data):
        snap = SnapshotRestore()
        snap.rollbacksnapshotrestore(data)
        return data

    def snapshotrestore(self, data):
        restore = SnapshotRestore()
        res = restore.restoreIncrementSnap(data)
        if not res:
            self.rollback(data)
        return data

    def snapshotrestorefull(self, data):
        restore = SnapshotRestore()
        res = restore.restoreFullSnap(data)
        if not res:
            self.rollback(data)
        return data


    def metadataupdate(self, data):
        logger.info("metadataupdate")

        return data

    def nfsmount(self, data):
        logger.info("nfs mount")
        backupstorage = BackupStorage()
        nfs_server = data.get('nfs_server')
        export_path = data.get('export_path')
        mount_path = data.get('mount_path')
        divicelist, ismount = backupstorage.nfsmount(nfs_server, export_path, mount_path)
        data['nfs'] = {'divicelist': divicelist, 'isnfsmount': ismount}
        return data

    def nfsunmount(self, data):
        logger.info("nfs unmount")
        backupstorage = BackupStorage()
        nfs_server = data.get('nfs_server')
        export_path = data.get('export_path')
        mount_path = data.get('mount_path')
        ismount = backupstorage.nfsunmount(nfs_server, export_path, mount_path)
        data['nfs']['isnfsmount'] = ismount
        return data


