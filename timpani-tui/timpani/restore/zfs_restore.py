import subprocess
import time
import os
from ast import literal_eval

from ..parser.sh_parser import ShellParser
from ..constants import Constants


class ZfsRestore:

    @staticmethod
    def get_restore_snapshot(node_name):
        result = os.listdir('/data/backup/{}'.format(node_name))

        return result

    def __init__(self, d, backup_node, backup_ip, snapshot_tag, target_node, target_ip):
        self.d = d
        self.backup_node = backup_node
        self.backup_ip = backup_ip
        self.snapshot_tag = snapshot_tag
        self.restore_path = Constants.RESTORE_PATH.format(self.backup_node, self.snapshot_tag)
        self.target_node = target_node
        self.target_ip = target_ip

        self.remain_pool_lst = []

        with open(self.restore_path + '{}_pool'.format(self.snapshot_tag), 'r') as f:
            self.backup_pool_list = [list(literal_eval(line)) for line in f][0]

    def _destroy_target_gpart(self):
        for geom in self.target_geom_list:
            result = subprocess.run('ssh root@{} gpart destroy -F {}'.format(self.target_ip, geom), shell=True, encoding='utf8', capture_output=True)
            _ = result.stderr
            _ = result.stdout

        # return error or stdout

    def _destroy_target_pool(self):
        for pool in self.target_pool_list:
            result = subprocess.run('ssh root@{} zpool destroy -f {}'.format(self.target_ip, pool), shell=True, encoding='utf8', capture_output=True)
            _ = result.stderr
            _ = result.stdout
        
        # return error or stdout

    def prepare_restore(self):
        self.d.infobox(
            Constants.RESTORE_START_MSG.format(self.target_node, self.backup_node, self.snapshot_tag),
            title='Information'
        )

        self.target_geom_list = ShellParser.geom_disk_parser(self.target_ip)
        self.target_geom_list.sort()

        tmp = ShellParser.zpool_list_parser(self.target_ip)
        if type(tmp) is not list:
            self.target_pool_list = [pool['pool'] for pool in self.backup_pool_list]
        else:
            self.target_pool_list = [pool['pool'] for pool in tmp]

        self._destroy_target_pool()
        self._destroy_target_gpart()

    def _add_raid_pool(self, pool, pool_data):
        _ = subprocess.run(
            'ssh root@{} zpool add -f {} {} {}'.format(
                self.target_ip, pool, pool_data['method'],' '.join(pool_data['device'])
            )
        )

    def _add_stripe_pool(self, pool, pool_data):
        _ = subprocess.run(
            'ssh root@{} zpool add -f {} {}'.format(
                self.target_ip, pool, ' '.join(pool_data['device'])
            )
        )

    def _create_boot_pool(self):      
        bootfs_list = ShellParser.get_bootfs_parser(self.backup_ip)
        self.bootfs = bootfs_list[0]
        self.boot_path = bootfs_list[2]
        for backup_pool in self.backup_pool_list:
            if backup_pool['pool'] == self.bootfs:
                first_restore_pool = backup_pool
    
        for idx, pool_data in enumerate(first_restore_pool['pool_data']):
            if pool_data['method'] == 'stripe':
                _ = subprocess.run(
                    'ssh root@{} zpool create -f {} {}'.format(
                        self.target_ip, first_restore_pool['pool'], ' '.join(pool_data['device'])
                    ), 
                    shell=True, encoding='utf8', capture_output=True
                )
                self.boot_device = pool_data['device'][0][:-2]
                if idx != 0:
                    self._add_stripe_pool(first_restore_pool['pool'], pool_data)

            elif 'raidz' in pool_data['method']:
                _ = subprocess.run(
                    'ssh root@{} zpool create -f {} {} {}'.format(
                        self.target_ip, first_restore_pool['pool'], pool_data['method'],  ' '.join(pool_data['device'])
                    ),
                    shell=True, encoding='utf8', capture_output=True
                )
                self.boot_device = pool_data['device'][0][:-2]
                if idx != 0:
                    self._add_raid_pool(first_restore_pool['pool'], pool_data)


    def _change_ashift_value(self):
        with open(self.restore_path + '{}_ashift_value'.format(self.snapshot_tag), 'r') as f:
            backup_ashift_value = f.read()
        result = subprocess.run(
            'ssh root@{} sysctl vfs.zfs.min_auto_ashift={}'.format(
                self.target_ip, backup_ashift_value
            ),
            shell=True, encoding='utf8', capture_output=True
        )
        _ = result.stdout
        _ = result.stderr

    def _create_gpart(self):
        backup_gpart_list = os.listdir(self.restore_path + 'gpart')
        backup_gpart_list.sort()

        for idx in range(len(self.target_geom_list)):
            result = subprocess.run(
                'ssh root@{} "gpart restore {}" < {}{}'.format(
                    self.target_ip, 
                    self.target_geom_list[idx], 
                    self.restore_path + 'gpart/', 
                    backup_gpart_list[idx]
                ), 
                shell=True, encoding='utf8', capture_output=True
            )
            _ = result.stderr
            _ = result.stdout

        self._change_ashift_value()

    def _restore_boot_pool(self):
        restore_pool_path = self.restore_path + '{}_{}.zfs.bz2'.format(self.snapshot_tag, self.bootfs)
        subprocess.run(
            'cat {} | bunzip2 | ssh root@{} "zfs receive" -vF {}'.format(
                restore_pool_path, self.target_ip, self.bootfs
            ),
            shell=True, encoding='utf8'
        )
        
        _ = subprocess.run(
            'ssh root@{} gpart bootcode -b /boot/pmbr -p /boot/gptzfsboot -i 1 {}'.format(
                self.target_ip, self.boot_device
            ),
            shell=True, encoding='utf8', capture_output=True
        )

        _ = subprocess.run(
            'ssh root@{} "zpool set bootfs={} {}"'.format(
                self.target_ip, self.boot_path, self.bootfs
            ),
            shell=True, encoding='utf8', capture_output=True
        )

        self.d.infobox(
            Constants.RESTORE_REBOOT_MSG.format(self.target_node),
            title='Information'
        )
        time.sleep(1)

        _ = subprocess.run(
            'ssh root@{} reboot'.format(self.target_ip), shell=True, encoding='utf8', capture_output=True
        )
        time.sleep(2)

    def _create_remain_pool(self):
        for remain_pool in self.backup_pool_list:
            if remain_pool['pool'] == self.bootfs:
                continue
            else:
                for idx, pool_data in enumerate(remain_pool['pool_data']):
                    if idx == 0:
                        _ = subprocess.run(
                            'ssh root@{} zpool destroy -f {}'.format(
                                self.target_ip, remain_pool['pool']
                            ),
                            shell=True, encoding='utf8', capture_output=True
                        )

                    self.remain_pool_lst.append(remain_pool['pool'])
                    if pool_data['method'] == 'stripe':
                        _ = subprocess.run(
                            'ssh root@{} zpool create -f {} {}'.format(
                                self.target_ip, remain_pool['pool'], ' '.join(pool_data['device'])
                            ),
                            shell=True, encoding='utf8', capture_output=True
                        )
                        if idx != 0:
                            self._add_stripe_pool(remain_pool['pool'], pool_data)
                    elif 'radiz' in pool_data['method']:
                        _ = subprocess.run(
                            'ssh root@{} zpool create -f {} {} {}'.format(
                                self.target_ip, remain_pool['pool'], pool_data['method'], ' '.join(pool_data['device'])
                            ),
                            shell=True, encoding='utf8', capture_output=True
                        )
                        if idx != 0:
                            self._add_raid_pool(remain_pool['pool'], pool_data)

    def _restore_remain_pool(self):
        for pool in self.remain_pool_lst:
            restore_pool_path = self.restore_path + '{}_{}.zfs.bz2'.format(self.snapshot_tag, pool)

            subprocess.run(
                'cat {} | bunzip2 | ssh root@{} "zfs receive" -vF {}'.format(
                    restore_pool_path, self.target_ip, pool
                ),
                shell=True, encoding='utf8'
            )
            self.d.infobox(
                Constants.RESTORE_FINISH_MSG,
                title='Information'
            )
            time.sleep(2)

    def _check_target_node_alive(self):
        _ = subprocess.run('ssh-keygen -R {}'.format(self.target_ip), shell=True, encoding='utf8', capture_output=True)
        while True:
            try:
                result = subprocess.run('ssh root@{} hostname'.format(self.target_ip), timeout=2, shell=True, encoding='utf8', capture_output=True)
                if not result.stderr:
                    self.d.infobox(
                        Constants.RESTORE_REMAIN_POOL,
                        title='Information'
                    )
                    time.sleep(1)
                    break
            except subprocess.TimeoutExpired as e:
                time.sleep(10)
                _ = e        

    def restore_runner(self):
        self._create_gpart()
        self._create_boot_pool()
        self._restore_boot_pool()
        self._check_target_node_alive()
        self._create_remain_pool()
        self._restore_remain_pool()
