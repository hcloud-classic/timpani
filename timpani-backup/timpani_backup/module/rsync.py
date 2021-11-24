import logging
import datetime
import re
import subprocess

from ..util.systemutil import Systemutil

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
stream_hander.setLevel(level=logging.INFO)
logger.addHandler(stream_hander)

class RsyncRun(object):

    OS_RSYNC_EXCLUDE = [
        "/dev/*",
        "/proc/*",
        "/sys/*",
        "/tmp/*",
        "/run/*",
        "/mnt/*",
        "/media/*",
        "/lost+found",
        "/var/cache/*",
        "/var/backup/*",
        "/var/backups/*",
        "/var/crash/*",
        "/var/tmp/*",
        "/var/spool/*",
        "/var/run/*",
        "/var/log/*",
        "/var/lib/lxcfs/cgroup/*",
        "/swapfile",
        ".cache",
        ".zfs"
    ]

    def getNowStr(self, node_name):
        now = datetime.datetime.now()
        nowDate = now.strftime('%Y%m%d%H%M%S')
        day = nowDate[:8]
        time = nowDate[8:]
        res = node_name[:8] + "-" + nowDate
        logger.info("day : {}, time : {}".format(day, time))
        return res, day, time

    def run(self,cmd):

        try:
            process = subprocess.Popen(cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            returncode = process.wait()
        except subprocess.CalledProcessError as e:
            raise e

        return process.stdout.read()

    def check_dir_ubuntu(self, mount_path, uuid, snapname):
        home_dir = mount_path + '/' + uuid
        part_dir = home_dir + '/part/' + snapname
        snap_dir = home_dir + '/snap/SR'
        snapname_dir = snap_dir + '/'+snapname
        systemutil = Systemutil()
        systemutil.dirExistCheckAndCreate(home_dir)
        systemutil.dirExistCheckAndCreate(part_dir)
        systemutil.dirExistCheckAndCreate(snap_dir)
        systemutil.dirExistCheckAndCreate(snapname_dir)
        part_path = '/' + uuid + '/part/' + snapname
        snapname_path = '/' + uuid + '/snap/SR/' +snapname
        return part_dir, snapname_dir, part_path, snapname_path

    def rsyncosbackup(self, data):
        snapname, day, nowtime = self.getNowStr(data.get('target_uuid'))
        target_uuid = data.get('target_uuid').upper()
        mount_path = data.get('mount_path')
        save_part, save_snapshot, db_part, db_snapshot = self.check_dir_ubuntu(data.get('mount_path'), target_uuid,
                                                                                snapname)
        dbmetadata = data.get('dbmetadata')
        link_dest_pre = None
        priv_snapfilename = None
        priv_snapfullname = None
        if dbmetadata is not None:
            priv_snapdata = data.get('dbmetadata').get('snapdata')
            if priv_snapdata is not None:
                link_dest_pre = priv_snapdata.get('save_path')
                priv_snapfilename = priv_snapdata.get('snapfilename')
                priv_snapfullname = priv_snapdata.get('snapfullname')

        exclude_list = data.get('exclude_list')
        for exclude_path in exclude_list:
            self.OS_RSYNC_EXCLUDE.append(exclude_path)
        self.OS_RSYNC_EXCLUDE.append(mount_path)

        exclude = ""
        for exclude_v in self.OS_RSYNC_EXCLUDE:
            exclude = "{} --exclude={}".format(exclude, exclude_v)

        target = data.get('name')
        if len(target) > 1:
            target += '/'

        try:
            cmd = None
            if link_dest_pre is not None:
                link_dest = mount_path + link_dest_pre
                cmd = "rsync -aAXz --delete {target} --link-dest={link_dest} {exclude} {snap_path}".format(target=target, link_dest=link_dest, exclude=exclude, snap_path=save_snapshot)
            else:
                cmd = "rsync -aAXz --delete {target} {exclude} {snap_path}".format(target=target, exclude=exclude, snap_path=save_snapshot)

            logger.info("shell cmd : {}".format(cmd))
            out = self.run(cmd)
        except:
            errcode = '4020'
            errstr = 'SnapShot File Transfer Failed'
            return {'error_code':errcode, 'error_message':errstr}

        dataset = target
        isfull = 1

        return {'dataset': dataset, 'snapname': snapname, 'snapfilename': snapname,
                'snapfullname': snapname,
                'priv_snapfilename': priv_snapfilename, 'priv_snapfullname': priv_snapfullname,
                'part_path': db_part, 'isfull': isfull, 'save_path':db_snapshot}


    def rsyncdatabackup(self, data):
        snapname, day, nowtime = self.getNowStr(data.get('target_uuid'))
        target_uuid = data.get('target_uuid').upper()
        mount_path = data.get('mount_path')
        save_part, save_snapshot, db_part, db_snapshot = self.check_dir_ubuntu(data.get('mount_path'), target_uuid,
                                                                                snapname)
        dbmetadata = data.get('dbmetadata')
        link_dest_pre = None
        priv_snapfilename = None
        priv_snapfullname = None
        if dbmetadata is not None:
            priv_snapdata = data.get('dbmetadata').get('snapdata')
            if priv_snapdata is not None:
                link_dest_pre = priv_snapdata.get('save_path')
                priv_snapfilename = priv_snapdata.get('snapfilename')
                priv_snapfullname = priv_snapdata.get('snapfullname')

        self.OS_RSYNC_EXCLUDE.append(mount_path)

        exclude = ""
        for exclude_v in self.OS_RSYNC_EXCLUDE:
            exclude = "{} --exclude={}".format(exclude, exclude_v)
        target = data.get('name')

        try:
            cmd = None
            if link_dest_pre is not None:
                link_dest = mount_path + link_dest_pre
                cmd = "rsync -aAXz --delete --link-dest={link_dest} {target}/ {snap_path}".format(link_dest=link_dest,
                                                                                                    target=target,
                                                                                                    snap_path=save_snapshot)
            else:
                cmd = "rsync -aAXz --delete {target}/ {snap_path}".format(target=target, snap_path=save_snapshot)

            logger.info("shell cmd : {}".format(cmd))
            out = self.run(cmd)
        except Exception as e:
            errcode = '4020'
            errstr = 'SnapShot File Transfer Failed'
            logger.info(e)
            return {'error_code': errcode, 'error_message': errstr}

        if data.get('name').__eq__('-'):
            dataset = "data_master"
        else:
            dataset = data.get('name')

        isfull = 1

        return {'dataset': dataset, 'snapname': snapname, 'snapfilename': snapname,
                'snapfullname': snapname,
                'priv_snapfilename': priv_snapfilename, 'priv_snapfullname': priv_snapfullname,
                'part_path': db_part, 'isfull': isfull, 'save_path': db_snapshot}

    def rsyncdatarestore(self, data):

        target_uuid = data.get('target_uuid').upper()
        mount_path = data.get('mount_path')

        dataset = data.get('name')                      # TARGET DIR
        snapdata = data.get('restoredata').get('target_snapdata').get('snapdata')
        snap_path = snapdata.get('save_path')
        link_dest = mount_path + snap_path

        try:
            # Rsync Recover
            cmd = "rsync -aAXz --delete {link_dest}/ {remote_backup_path} ".format(remote_backup_path=dataset, link_dest=link_dest)
            logger.info("shell cmd : {}".format(cmd))
            out = self.run(cmd)
            logger.info("[rsyncdatarestore] run STDOUT : {}".format(out))
        except Exception as e:
            logger.info("[rsyncdatarestore] Exception : {}".format(e))
            errcode = '4020'
            errstr = 'SnapShot File Transfer Failed'
            return {'error_code': errcode, 'error_message': errstr}

        return data

    def rsyncosrestore(self, data):

        target_uuid = data.get('target_uuid').upper()
        mount_path = data.get('mount_path')

        dataset = data.get('name')  # TARGET DIR
        snapdata = data.get('restoredata').get('target_snapdata').get('snapdata')
        snap_path = snapdata.get('save_path')
        link_dest = mount_path + snap_path

        try:
            # Rsync Recover
            cmd = "rsync -aAXz --delete {link_dest}/ {remote_backup_path} ".format(remote_backup_path=dataset,
                                                                                   link_dest=link_dest)
            logger.info("shell cmd : {}".format(cmd))
            out = self.run(cmd)

        except Exception as e:
            logger.info("[rsyncosrestore] Exception : {}".format(e))
            errcode = '4020'
            errstr = 'SnapShot File Transfer Failed'
            return {'error_code': errcode, 'error_message': errstr}

        return data

