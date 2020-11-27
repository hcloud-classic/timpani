from ..constants import Constants
from ..db.database import Database
from dialog import Dialog
from .zfs import BackupZfs

import time


class FullBackup(object):
    def __init__(self, d, db):
        self.d = d
        self.db = db

    def backup_status_list(self, node_name):
        result = BackupZfs.zfs_backup_status_list(node_name)
        self.d.scrollbox(result)

    def detail_information(self, node_name):
        node_ip = self.db.select(node_name)[-1]['ip']
        code, tag = self.d.menu(
            "Please select",
            choices=Constants.BACKUP_DETAIL_MENU
        )

        if code == self.d.OK:
            if tag.__eq__('1'):
                result = BackupZfs.zpool_status(node_ip)
                self.d.scrollbox(result)
            elif tag.__eq__('2'):
                result = BackupZfs.zpool_list(node_ip)
                self.d.scrollbox(result)
            elif tag.__eq__('3'):
                result = BackupZfs.zfs_list(node_ip)
                self.d.scrollbox(result)
            elif tag.__eq__('4'):
                result = BackupZfs.gpart_show_status(node_ip)
                self.d.scrollbox(result)
            elif tag.__eq__('5'):
                result = BackupZfs.gpart_list(node_ip)
                self.d.scrollbox(result)
            elif tag.__eq__('6'):
                result = BackupZfs.zfs_space(node_ip)
                self.d.scrollbox(result)
            self.detail_information(node_name)
        return            
            
    def backup(self, node_name):
        self.d.set_background_title('{} Node Backup'.format(node_name))
        code = self.d.yesno(Constants.BACKUP_CHECK_MSG.format(node_name))
        if code == self.d.OK:
            from datetime import datetime
            file_name = datetime.today().strftime("%Y%m%d")
            code = self.d.yesno(Constants.BACKUP_INIT_MSG.format(node_name, file_name, node_name, file_name))

            if code == self.d.OK:
                node_ip = self.db.select(node_name)[-1]['ip']
                _ = BackupZfs.zfs_run_backup_snapshot(node_name, node_ip)
            
            return

    def backup_description(self, node_name):
        self.d.set_background_title('{} Node'.format(node_name))
        code, tag = self.d.menu(
            "Please select:",
            choices=Constants.BACKUP_MENU
        )

        if code == self.d.OK:
            if tag.__eq__('1'):
                self.backup_status_list(node_name)
            elif tag.__eq__('2'):
                self.detail_information(node_name)
            elif tag.__eq__('3'):
                self.backup(node_name)
            self.backup_description(node_name)
        return

    def backup_menu(self):
        result = self.db.select()
        if not result:
            self.d.infobox(
                "There is no registered node.",
                title="Information"
            )
            time.sleep(2)
            return
        
        else:
            for i in result:
                del i["ip"]
                temp_list = list(i.values())
                temp_list.append(False)
                Constants.NODE_LIST.append(tuple(temp_list))

            code, tag = self.d.radiolist(
                "You can select node:",
                choices=Constants.NODE_LIST
            )
            del Constants.NODE_LIST[:]

            if code == self.d.OK:
                if tag != "":
                    self.backup_description(tag)
                return
            elif code == self.d.CANCEL:
                return
