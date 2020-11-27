from ..constants import Constants
from ..db.database import Database
from ..fbackup.zfs import BackupZfs
from .zfs_restore import ZfsRestore
from dialog import Dialog

import time


class Restore(object):
    def __init__(self, d, db):
        self.d = d
        self.restore_snapshot = ""
        self.db = db

    def backup_status_list(self, node_name):
        result = BackupZfs.zfs_backup_status_list(node_name)
        self.d.scrollbox(result)

    def select_restore_snapshot(self, node_name):
        self.d.set_background_title('Select Snapshot')
        result = ZfsRestore.get_restore_snapshot(node_name)

        # del result[-1]
        
        if not result:
            self.d.infobox(
                "There is no snapshot",
                title="Information"
            )
            time.sleep(2)
        else:
            snapshot_list = [tuple((i, 'snapshot', False)) for i in result]
            code, tag = self.d.radiolist(
                "You can select Snapshot",
                choices=snapshot_list
            )
            if code == self.d.OK:
                if tag !="":
                    self.restore_snapshot = tag
                return
            else:
                return

    def boot_restore(self, node_name):
        if self.restore_snapshot == "":
            self.d.infobox(
                Constants.RESTORE_CHECK_MSG,
                title="Information"
            )
            time.sleep(2)
            return

        code, node_info = self.d.form(
            "Insert Restore Node Information",
            elements=Constants.RESTORE_TARGET_NODE
        )
        if code == self.d.OK:
            if "" not in node_info:
                # node name and node description (restore target)
                target_node = node_info[0]
                # _ = node_info[2]
                target_ip = node_info[1]
            else:
                return
        else:
            return

        self.d.set_background_title('{} Node Restore'.format(target_node))
        code = self.d.yesno(
            Constants.RESTORE_INIT_MSG.format(target_node, node_name, self.restore_snapshot),
            title="Restore"
            )

        if code == self.d.OK:
            node_ip = self.db.select(node_name)[-1]['ip']
            zfsrestore = ZfsRestore(self.d, node_name, node_ip, self.restore_snapshot, target_node, target_ip)
            zfsrestore.prepare_restore()
            zfsrestore.restore_runner()

    
    """
    def other_restore(self, node_name):
        pass
    """

    def restore_description(self, node_name):
        self.d.set_background_title('{} Node'.format(node_name))
        code, tag = self.d.menu(
            "Please select:",
            choices=Constants.RESTORE_MENU
        )

        if code == self.d.OK:
            if tag.__eq__('1'):
                self.backup_status_list(node_name)
            elif tag.__eq__('2'):
                self.select_restore_snapshot(node_name)
            elif tag.__eq__('3'):
                self.boot_restore(node_name)
            # elif tag.__eq__('4'):
            #     self.other_restore(node_name)
            self.restore_description(node_name)
        return

    def restore_menu(self):
        result = self.db.select()
        if not result:
            self.d.infobox(
                "There is no registered node.",
                title="Information"
            )
            time.sleep(2)
            return
        else:
            self.d.set_background_title('Select Restore Node')
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
                self.restore_description(tag)
            return
        elif code == self.d.CANCEL:
            return
