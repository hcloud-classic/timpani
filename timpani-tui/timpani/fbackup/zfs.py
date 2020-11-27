import subprocess
from datetime import datetime

from ..constants import Constants
from ..parser.sh_parser import ShellParser


class BackupZfs:
    
    @staticmethod
    def _save_backup_information(node_name, kinds, result):
        date = datetime.today().strftime("%Y%m%d")
        if kinds not in Constants.BACKUP_SAVE_FILE:
            backup_path = Constants.DEFAULT_PATH + '{}/{}/gpart/{}_{}'.format(node_name, date, date, kinds)
        else:    
            backup_path = Constants.DEFAULT_PATH + '{}/{}/{}_{}'.format(node_name, date, date, kinds)
        with open(backup_path, 'a') as f:
            f.write(str(result))

    @staticmethod
    def _zfs_get_pool_name(node_name, ip):
        result = ShellParser.zpool_list_parser(ip)
        BackupZfs._save_backup_information(node_name, 'pool', result)
        pool_list = [i['pool'] for i in result]

        return pool_list

    @staticmethod
    def zpool_status(node_ip):
        result = subprocess.run('ssh root@{} "zpool status"'.format(node_ip), shell=True, encoding='utf8', capture_output=True).stdout
        return result

    @staticmethod
    def zpool_list(node_ip):
        result = subprocess.run('ssh root@{} "zpool list"'.format(node_ip), shell=True, encoding='utf8', capture_output=True).stdout
        return result

    @staticmethod
    def zfs_list(node_ip):
        result = subprocess.run('ssh root@{} "zfs list"'.format(node_ip), shell=True, encoding='utf8', capture_output=True).stdout
        return result

    @staticmethod
    def gpart_show_status(node_ip):
        result = "-------------gpart show------------- \n"
        result += subprocess.run('ssh root@{} "gpart show"'.format(node_ip), shell=True, encoding='utf8', capture_output=True).stdout
        result += "------------gpart status------------ \n"
        result += subprocess.run('ssh root@{} "gpart status"'.format(node_ip), shell=True, encoding='utf8', capture_output=True).stdout
        return result
    
    @staticmethod
    def gpart_list(node_ip):
        result = subprocess.run('ssh root@{} "gpart list"'.format(node_ip), shell=True, encoding='utf8', capture_output=True).stdout
        return result

    @staticmethod
    def zfs_space(node_ip):
        result = subprocess.run('ssh root@{} "zfs list -o space"'.format(node_ip), shell=True, encoding='utf8', capture_output=True).stdout
        return result
    
    @staticmethod
    def zfs_backup_status_list(node_name):
        result = subprocess.run('tree --du -h /data/backup/{}'.format(node_name), shell=True, encoding='utf8', capture_output=True).stdout
        return result

    @staticmethod
    def zfs_backup_gpart(node_name, ip):
        geom_list = ShellParser.geom_disk_parser(ip)
        BackupZfs._save_backup_information(node_name, 'geom_list', geom_list)

        for geom in geom_list:
            temp_geom = subprocess.run('ssh root@{} gpart backup {}'.format(ip, geom), shell=True, encoding='utf8', capture_output=True)
            _ = temp_geom.stderr
            BackupZfs._save_backup_information(node_name, geom, temp_geom.stdout)

    @staticmethod
    def zfs_get_ashift_value(node_name, ip):
        result = subprocess.run('ssh root@{} "sysctl -a | grep min_auto_ashift"'.format(ip), shell=True, encoding='utf8', capture_output=True)
        _ = result.stderr
        ashift_value = ShellParser.ashift_value_parser(result.stdout)
        BackupZfs._save_backup_information(node_name, 'ashift_value', ashift_value)

    @staticmethod
    def zfs_run_backup_snapshot(node_name, ip):
        date = datetime.today().strftime("%Y%m%d")
        subprocess.call('mkdir -p /data/backup/{}/{}/gpart'.format(node_name, date), shell=True)
        pool_list = BackupZfs._zfs_get_pool_name(node_name, ip)
        BackupZfs.zfs_backup_gpart(node_name, ip)
        BackupZfs.zfs_get_ashift_value(node_name, ip)

        for pool in pool_list:
            subprocess.call('ssh root@{} "zfs snapshot -r {}@{}"'.format(ip, pool, date), shell=True)
            subprocess.call('ssh root@{} "zfs send -Rv {}@{}" | bzip2 | ssh root@{} "cat > /data/backup/{}/{}/{}_{}.zfs.bz2"'.format(ip, pool, date, Constants.HOST_IP, node_name, date, date, pool), shell=True)
            subprocess.call('ssh root@{} "zfs destroy -r {}@{}"'.format(ip, pool, date), shell=True)

        return Constants.BACKUP_FINISH_MSG.format(node_name)
