import logging
import re
import copy
import os
import datetime
from ..zfs import ZFS
from ..util.systemutil import Systemutil

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
stream_hander.setLevel(level=logging.INFO)
logger.addHandler(stream_hander)

class Snapshot(object):

    systemutil = Systemutil()

    def getNowStr(self, node_name):
        now = datetime.datetime.now()
        nowDate = now.strftime('%Y%m%d%H%M%S')
        day = nowDate[:8]
        time = nowDate[8:]
        res = node_name[:8] + "-" + nowDate
        logger.info("day : {}, time : {}".format(day, time))
        return res, day, time

    # DIR STRUCT
      # UBUNTU : <NFS MOUNT>/<UUID>/part
      #                            /snap/SR/<snapname>
      # FREEBSD : <NFS MOUNT>/<UUID>/part
      #                             /snap/SZ/<snapname>/<full snapshot filename>

    def check_dir_ubuntu(self, mount_path, uuid, snapname):
        home_dir = mount_path + '/' + uuid
        part_dir = home_dir + '/part/' + snapname
        snap_dir = home_dir + '/snap/SR'
        snapname_dir = snap_dir + '/'+snapname
        self.systemutil.dirExistCheckAndCreate(home_dir)
        self.systemutil.dirExistCheckAndCreate(part_dir)
        self.systemutil.dirExistCheckAndCreate(snap_dir)
        self.systemutil.dirExistCheckAndCreate(snapname_dir)
        part_path = '/' + uuid + '/part/' + snapname
        snapname_path = '/' + uuid + '/snap/SR/' +snapname
        return part_dir, snapname_dir, part_path, snapname_path

    def check_dir_freebsd(self, mount_path, uuid, snapname):
        home_dir = mount_path + '/' + uuid
        part_dir = home_dir + '/part/' + snapname
        snap_dir = home_dir + '/snap/SZ'
        snapname_dir = snap_dir + '/'+snapname
        self.systemutil.dirExistCheckAndCreate(home_dir)
        self.systemutil.dirExistCheckAndCreate(part_dir)
        self.systemutil.dirExistCheckAndCreate(snap_dir)
        self.systemutil.dirExistCheckAndCreate(snapname_dir)

        part_path = '/'+uuid+'/part/' + snapname
        snapname_path = '/'+uuid+'/snap/SZ/' + snapname
        return part_dir, snapname_dir, part_path, snapname_path

    def rename_dir_freebsd(self, mount_path, uuid, snapname):
        home_dir = mount_path + '/' + uuid
        snap_dir = home_dir + '/snap/SZ'
        snapname_dir = snap_dir + '/'+ snapname + '_rollback'
        self.systemutil.dirExistCheckAndCreate(home_dir)
        self.systemutil.dirExistCheckAndCreate(snap_dir)
        self.systemutil.dirExistCheckAndCreate(snapname_dir)

        return snapname_dir

    def databackup(self, data, snapname, lastsnapname):
        nodetype = data.get('nodetype')
        server_uuid = data.get('server_uuid').replace('-', '').upper()
        target_uuid = data.get('target_uuid').upper()
        cur_collectdata = data.get('cur_collectdata')
        target_datasetlist = cur_collectdata.get('target_datasetlist')
        snapshotlist = cur_collectdata.get('cur_snaplist')
        cur_lastsnapname = None
        priv_snapfilename = data.get('priv_snapfilename')
        priv_snapfullname = data.get('priv_snapfullname')
        devlist = cur_collectdata.get('cur_devlist')

        snapfilelist = []

        logger.info("data : {}".format(data))
        logger.info("cur_collectdata : {}".format(cur_collectdata))
        logger.info("target_datalist : {}".format(target_datasetlist))
        if nodetype.upper().__eq__('MASTER'):
            logger.info("nodetype : {}".format(nodetype))
            save_part, save_snapshot, db_part, db_snapshot = self.check_dir_ubuntu(data.get('mount_path'), target_uuid, snapname)

            logger.info("nodetype : {}, save_part :{}, save_snapshot : {}".format(nodetype, save_part, save_snapshot))
        else:
            logger.info("[NOT MASTER] nodetype : {}".format(nodetype))
            save_part, save_snapshot, db_part, db_snapshot = self.check_dir_freebsd(data.get('mount_path'), target_uuid, snapname)
            logger.info("nodetype: {}, save_part :{}, save_snapshot : {}\n datasetlist : {}".format(nodetype, save_part, save_snapshot, target_datasetlist))
            for pool, dataset in target_datasetlist:
                try:
                    logger.info("datalist : pool : {}, dataset : {}".format(pool, dataset))
                    ZFS.zfs_snapshot(filesystem=dataset, snapname=snapname, recursive=False)
                    snapfilename = dataset.replace('/','_') + "@" + snapname
                    snapfullname = dataset+"@"+snapname
                    if priv_snapfullname is None:
                        isfull = 1
                    else:
                        isfull = 0
                    snapfilelist.append({'dataset':dataset, 'snapname': snapname, 'snapfilename':snapfilename, 'snapfullname': snapfullname,
                                         'priv_snapfilename': priv_snapfilename, 'priv_snapfullname': priv_snapfullname,
                                         'part_path': db_part, 'isfull': isfull})
                except Exception as e:
                    logger.info("[databackup] EXCEPT : {}".format(e))

        data['part_path'] = {'save_part': save_part, 'db_part': db_part}

        for snapfile in snapfilelist:
            try:
                remote_path = save_snapshot + "/" + snapfile.get('snapfilename')
                ZFS.zfs_send_local(send_target=snapfile.get('snapfullname'),
                                   parent_target=priv_snapfullname,
                                   remote_path=remote_path,
                                   isfull = False,
                                   isdata = True,
                                   isgzip = True
                                   )
            except Exception as e:
                logger.info("[databackup] EXCEPT : {}".format(e))
            snapfile['save_path'] = db_snapshot + '/' + snapfile.get('snapfilename') + ".zfs.gz"
            check_file_path = remote_path + ".zfs.gz"
            f_size = os.path.getsize(check_file_path)
            logger.info("check file : {}\nfile size : {} {}".format(check_file_path, f_size, f_size/1024))
        logger.info("snapfilelist : {}".format(snapfilelist))

        return snapfilelist

    def osbackup(self, data, snapname):
        nodetype = data.get('nodetype')
        server_uuid = data.get('server_uuid').replace('-', '').upper()
        target_uuid = data.get('target_uuid').upper()
        cur_collectdata = data.get('cur_collectdata')
        target_datasetlist = cur_collectdata.get('target_datasetlist')
        snapshotlist = cur_collectdata.get('cur_snaplist')
        cur_lastsnapname = None
        priv_snapfilename = data.get('priv_snapfilename')
        priv_snapfullname = data.get('priv_snapfullname')
        devlist = cur_collectdata.get('cur_devlist')

        snapfilelist = []

        logger.info("data : {}".format(data))
        logger.info("cur_collectdata : {}".format(cur_collectdata))
        logger.info("target_datalist : {}".format(target_datasetlist))
        if nodetype.upper().__eq__('MASTER'):
            logger.info("nodetype : {}".format(nodetype))
            save_part, save_snapshot, db_part, db_snapshot = self.check_dir_ubuntu(data.get('mount_path'), target_uuid,
                                                                                   snapname)
            logger.info("nodetype : {}, save_part :{}, save_snapshot : {}".format(nodetype, save_part, save_snapshot))
        else:
            logger.info("[NOT MASTER] nodetype : {}".format(nodetype))
            save_part, save_snapshot, db_part, db_snapshot = self.check_dir_freebsd(data.get('mount_path'), target_uuid,
                                                                                    snapname)
            logger.info("nodetype: {}, save_part :{}, save_snapshot : {}\n datasetlist : {}".format(nodetype, save_part,
                                                                                                    save_snapshot,
                                                                                                    target_datasetlist))
            for pool, dataset in target_datasetlist:
                try:
                    logger.info("datalist : pool : {}, dataset : {}".format(pool, dataset))
                    ZFS.zfs_snapshot(filesystem=pool, snapname=snapname, recursive=True)
                    snapfilename = dataset.replace('/', '_') + "@" + snapname
                    snapfullname = dataset + "@" + snapname
                    if priv_snapfullname is None:
                        isfull = 1
                    else:
                        isfull = 0
                    snapfilelist.append({'dataset': dataset, 'snapname': snapname, 'snapfilename': snapfilename,
                                         'snapfullname': snapfullname,
                                         'priv_snapfilename': priv_snapfilename, 'priv_snapfullname': priv_snapfullname,
                                         'part_path': db_part, 'isfull': isfull})
                except Exception as e:
                    logger.info("[databackup] EXCEPT : {}".format(e))

                break

        data['part_path'] = {'save_part': save_part, 'db_part': db_part}

        for snapfile in snapfilelist:
            try:
                remote_path = save_snapshot + "/" + snapfile.get('snapfilename')
                ZFS.zfs_send_local(send_target=snapfile.get('snapfullname'),
                                   parent_target=priv_snapfullname,
                                   remote_path=remote_path,
                                   isfull=True,
                                   isdata=False,
                                   isgzip=True
                                   )
            except Exception as e:
                logger.info("[databackup] EXCEPT : {}".format(e))
            snapfile['save_path'] = db_snapshot + '/' + snapfile.get('snapfilename') + ".zfs.gz"
            check_file_path = remote_path + ".zfs.gz"
            f_size = os.path.getsize(check_file_path)
            logger.info("check file : {}\nfile size : {} {}".format(check_file_path, f_size, f_size / 1024))
        logger.info("snapfilelist : {}".format(snapfilelist))

        return snapfilelist

    def createsnapshot(self, data):
        usetype = data.get('usetype')
        nodetype = data.get('nodetype')

        snapname, day, nowtime = self.getNowStr(data.get('target_uuid'))

        if usetype.__eq__('DATA'):
            # increment backup
            snapmeta = self.databackup(data, snapname, None)
            data['save_snap_meta'] = snapmeta
        elif usetype.__eq__('ORIGIN'):
            # Fullbackup
            self.osbackup(data, snapname)
        elif usetype.__eq__('OS'):
            if nodetype.__eq__('COMPUTE'):
                snapmeta = self.databackup(data, snapname, None)
                data['save_snap_meta'] = snapmeta
            # Fullbackup
            else:
                snapmeta = self.osbackup(data, snapname)
                data['save_snap_meta'] = snapmeta

    def snapshot_destroy(self, snaplist, compare_snapname, isfull):
        for snapdata in snaplist:
            if not isfull:
                if snapdata.get('zfs_name').__eq__(compare_snapname):
                    return True
                else:
                    ZFS.zfs_destroy_snapshot(snapdata.get('zfs_name'))
            else:
                ZFS.zfs_destroy_snapshot(snapdata.get('zfs_name'), recursive_descendents=True)
        return False

    def destorysnapshot(self, data, isfull):
        prev_snaplist = data.get('cur_snaplist')
        check_snaplist = data.get('check_snaplist')
        meta_snap = data.get('save_snap_meta')
        for snap_meta in meta_snap:
            compare_snapfullname = snap_meta.get('snapfullname')
            try:
                self.snapshot_destroy(check_snaplist, compare_snapfullname, isfull)
            except Exception as e:
                logger.info("[databackup] EXCEPT : {}".format(e))

    def destorysnapshot_one(self, snapshot_name):
        try:
            ZFS.zfs_destroy_snapshot(snapshot_name)
            logger.info('{} snap destroy success'.format(snapshot_name))
        except Exception as e:
            logger.info('{} snap destroy failed'.format(snapshot_name))

    def destorysnapshotall(self, snapshotlist):
        for snapdata in snapshotlist:
            snapshot_name = snapdata.get('zfs_name')
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


