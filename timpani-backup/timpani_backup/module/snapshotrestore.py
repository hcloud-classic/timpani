import logging
import re
import copy
import os
import datetime
from ..zfs import ZFS
from .zvolmetadata import zvolMetaData
from ..util.systemutil import Systemutil

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
stream_hander.setLevel(level=logging.INFO)
logger.addHandler(stream_hander)

class SnapshotRestore(object):
    systemutil = Systemutil()

    def getNowStr(self, node_name):
        now = datetime.datetime.now()
        nowDate = now.strftime('%Y%m%d%H%M%S')
        day = nowDate[:8]
        time = nowDate[8:]
        res = node_name[:8] + "-" + nowDate
        logger.info("day : {}, time : {}".format(day, time))
        return res, day, time

    def destorysnapshot_one(self, snapshot_name):
        try:
            ZFS.zfs_destroy_snapshot(snapshot_name)
            logger.info('{} snap destroy success'.format(snapshot_name))
        except Exception as e:
            logger.info('{} snap destroy failed'.format(snapshot_name))

    def destorysnapshotall(self, snapname):
        try:
            ZFS.zfs_destroy_snapshot(snapname, recursive_descendents=True)
            logger.info('{} snap destroy success'.format(snapname))
        except Exception as e:
            logger.info('{} snap destroy failed'.format(snapname))

    def checkrestorevalue(self, restorelist, check_index, priv_check_snapfullname):

        for snapdata in restorelist:
            snapinfo = snapdata.get('snapinfo')
            priv_snapfullname = snapinfo.get('priv_snapfullname')
            snapfullname = snapinfo.get('snapfullname')
            snapinfo_index = snapinfo.get('index')
            isfull = snapinfo.get('isfull')
            logger.info("snapinfo_index : {} check_index : {}".format(snapinfo_index, check_index))


            logger.info("priv_check_snapfullname : {} priv_snapfullname : {}".format(priv_check_snapfullname, priv_snapfullname))
            if priv_check_snapfullname is None:
                check_ok = False
                if priv_snapfullname is None:
                    if isfull == 1:
                        check_ok = True
                        return check_ok, snapfullname, snapdata, isfull
            elif priv_check_snapfullname.__eq__(priv_snapfullname):
                check_ok = True
                return check_ok, snapfullname, snapdata, isfull
            else:
                check_ok = False

        return False, None, None, None


    def checkrestorelist(self, restorelist):

        priv_check_snapfullname = None
        check_ok = False
        check_list = []
        for cnt in range(0, len(restorelist)):
            check_cnt = cnt + 1
            check_ok, check_snapfullname, snapdata, isfull = self.checkrestorevalue(restorelist, check_cnt, priv_check_snapfullname)
            if check_ok:
                priv_check_snapfullname = check_snapfullname
                save_data = {'snapdata':snapdata, 'isfull':isfull, 'index': check_cnt}
                check_list.append(save_data)
            else:
                check_list = None
                break

        return check_ok, check_list

    def rollbacksnapshotcreate(self, data):
        # target ==> nfs mount
        mount_path = data.get('mount_path')
        save_path = data.get('restoredata').get('target_snapdata').get('snapdata').get('save_path')
        snapfilename = data.get('restoredata').get('target_snapdata').get('snapdata').get('snapfilename')
        dataset = data.get('restoredata').get('target_snapdata').get('snapdata').get('dataset')
        rollback_snapname = "rollback_snap"
        rollback_save_path = mount_path + save_path.replace(snapfilename, "tmp_rollback")
        data['rollback_save_path'] = rollback_save_path
        rollback_save_path = rollback_save_path.replace(".zfs.gz","")

        try:
            ZFS.zfs_snapshot(filesystem=dataset, snapname=rollback_snapname, recursive=False)
        except Exception as e:
            logger.info("[databackup] EXCEPT : {}".format(e))


        try:
            targetsnapname = dataset + "@" + rollback_snapname
            ZFS.zfs_send_local(send_target=targetsnapname,
                               parent_target=None,
                               remote_path=rollback_save_path,
                               isfull=False,
                               isdata=True,
                               isgzip=True
                               )
        except Exception as e:
            logger.info("[databackup] EXCEPT : {}".format(e))

        self.destorysnapshot_one(targetsnapname)

        data['rollback_save_path'] = rollback_save_path

        return data

    def rollbacksnapshotrestore(self, data):
        dataset = data.get('restoredata').get('target_snapdata').get('snapdata').get('dataset')
        rollback_save_path = data.get('rollback_save_path')
        try:
            ZFS.zfs_restore_local(target=dataset,
                               remote_path=rollback_save_path,
                               isfull=True,
                               isdata=False,
                               isgzip=True
                               )
        except Exception as e:
            logger.info("[databackup] EXCEPT : {}".format(e))

        return data



    def rollbacksnapshotdestroy(self, data):
        path = data.get('rollback_save_path')
        if os.path.isfile(path):
            os.remove(path)

        return os.path.isfile(path)


    def checkprivsnapanddestroy(self, priv_snap, meta):
        check_ok = False
        snaplist, snap_cnt = meta.check_zfssnapshotlist()
        if priv_snap is None:
            if snap_cnt == 0:
                check_ok = True
        else:
            if snap_cnt == 0:
                return False, snaplist

            for snapdata in snaplist:
                snap_name = snapdata.get('zfs_name')
                if snap_name.__eq__(priv_snap):
                    if snap_cnt == 1:
                        check_ok = True

        return check_ok, snaplist


    def restoreIncrementSnap(self, data):
        dataset = data.get('restoredata').get('target_snapdata').get('snapdata').get('dataset')
        mount_path = data.get('mount_path')
        restorelist = data.get('check_list')
        logging.info("\ndataset : {} mount_path : {}\n".format(dataset, mount_path))
        if restorelist is None:
            return False

        meta = zvolMetaData(dataset, False)
        for cnt in range(0, len(restorelist)):
            check_cnt = cnt + 1
            for rdata in restorelist:
                logger.info("===========================================================>")
                index = rdata.get('index')
                logging.info("\nrdata :\n {}\n".format(rdata))
                if index == check_cnt:
                    snapinfo = rdata.get('snapdata').get('snapinfo')
                    save_path = snapinfo.get('save_path')
                    priv_snap = snapinfo.get('priv_snapfullname')
                    target_file = mount_path + save_path
                    check_ok, destroylist = self.checkprivsnapanddestroy(priv_snap, meta)
                    if not check_ok and priv_snap is None:
                        check_ok = True
                        for target_snap in destroylist:
                            target = target_snap.get('zfs_name')
                            self.destorysnapshot_one(target)

                    if not check_ok:
                        logger.info("Restore Failed")
                        return False

                    try:
                        ZFS.zfs_restore_local(target=dataset,
                                remote_path=target_file,
                                isfull=False,
                                isdata=True,
                                isgzip=True
                        )
                    except Exception as e:
                        logger.info("[databackup] EXCEPT : {}".format(e))

                    snaplist, snap_cnt = meta.check_zfssnapshotlist()
                    if priv_snap is None:
                        if snap_cnt == 1:
                            check_ok = True
                    else:
                        if snap_cnt > 1:
                            check_ok = True

                    if check_ok:
                        if priv_snap is not None:
                            self.destorysnapshot_one(priv_snap)
                    else:
                        return False
                logger.info("===========================================================>")
        return True

    def restoreFullSnap(self, data):
        dataset = data.get('restoredata').get('target_snapdata').get('snapdata').get('dataset')
        mount_path = data.get('mount_path')
        snapname = data.get('restoredata').get('target_snapdata').get('snapdata').get('snapfullname')
        save_path = data.get('restoredata').get('target_snapdata').get('snapdata').get('save_path')
        target_file = mount_path + save_path
        logging.info("\nsnapname : {} mount_path : {}\ntarget_file : {}".format(snapname, mount_path, target_file))

        try:
            output = ZFS.zfs_restore_local(target=dataset,
                                  remote_path=target_file,
                                  isfull=False,
                                  isdata=False,
                                  isgzip=True
                                  )

            if 'cannot' in output:
                data['error'] = {'errorcode':'6423', 'errormsg' : 'restore failed'}
                logger.info(data.get('error'))
        except Exception as e:
            logger.info("[databackup] EXCEPT : {}".format(e))

        # Destory ALL
        self.destorysnapshotall(snapname)
        return True