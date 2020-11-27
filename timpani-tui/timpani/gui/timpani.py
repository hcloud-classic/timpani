import locale
import time
import sys

from ..constants import Constants
from dialog import Dialog
from ..fbackup.fullbackup import FullBackup
from ..restore.restore import Restore
from ..configure.node_config import NodeConfig
from ..db.database import Database


locale.setlocale(locale.LC_ALL, '')


class TimpaniGui(object):
    d = Dialog(dialog='dialog')
    d.set_background_title('TIMPANI Backup & Restore')

    def process_exit(self):
        self.d.infobox("Terminating Process...", width=0, height=0, title="Message")
        time.sleep(2)
        sys.exit(0)

    def main(self):
        self.d.set_background_title('TIMPANI Backup & Restore')
        code, tag = self.d.menu(
            "Please select:",
            choices=Constants.MAIN_MENU
        )
        self.db = Database('sqlite.db')

        if code == self.d.CANCEL:
            self.process_exit()
        
        if code == self.d.OK:
            if tag.__eq__('1'):
                sub_menu = FullBackup(self.d, self.db)
                sub_menu.backup_menu()
            elif tag.__eq__('2'):
                sub_menu = Restore(self.d, self.db)
                sub_menu.restore_menu()
            elif tag.__eq__('3'):
                sub_menu = NodeConfig(self.d, self.db)
                sub_menu.config_menu()
            self.main()