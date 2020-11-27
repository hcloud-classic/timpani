import os
from os.path import expanduser
from datetime import datetime

class Constants:
    
    """
    ---------------------------------------------------------
    Common Constants
    ---------------------------------------------------------
    """

    DIR_HOME = expanduser(".")
    MAIN_MENU = [
        ("1", "Full Backup"),
        ("2", "Restore"),
        ("3", "Configuration")
    ]
    HOST_IP = "192.168.0.45"
    NODE_LIST = []
    BACKUP_DATE = datetime.today().strftime("%Y%m%d")
    DEFAULT_PATH = '/data/backup/'

    """
    ----------------------------------------------------------
    Backup Constants
    ----------------------------------------------------------
    """

    BACKUP_MENU = [
        ("1", "Backup status list"),
        ("2", "Detail Information"),
        ("3", "Backup")
    ]
    BACKUP_STATUS_LIST = []
    BACKUP_DETAIL_MENU = [
        ("1", "Zpool status"),
        ("2", "Zpool list"),
        ("3", "Zfs list"),
        ("4", "gpart show & status"),
        ("5", "gpart list"),
        ("6", "Disk Space Accounting for ZFS")
    ]
    BACKUP_CHECK_MSG = "Are you sure you want to permanently {} node backup?"
    BACKUP_INIT_MSG = "{} Node Snapshot name is {}.bz2 and Backup directory is /d ata/backup/{}/{}"
    BACKUP_FINISH_MSG = "{} Node Backup Finish"
    BACKUP_SAVE_FILE = ['pool', 'ashift_value', 'geom_list']

    """
    ----------------------------------------------------------
    Restore Constants
    ----------------------------------------------------------
    """

    RESTORE_MENU = [
        ("1", "Backup status list"),
        ("2", "Select Restore snapshot"),
        ("3", "Boot Restore")
    ]
    RESTORE_TARGET_NODE =[
        ("Node Name",   1, 5, "", 1, 20, 18, 30),
        ("IP Address",  2, 5, "", 2, 20, 18, 30)
    ]
    RESTORE_CHECK_MSG = "Please select snapshot"
    RESTORE_INIT_MSG = "Are you sure you want to permanently {} node restore via {} node {} snapshot?"
    RESTORE_START_MSG = "Start restore {} node via {} {} snapshot"
    RESTORE_PATH = "/data/backup/{}/{}/"
    RESTORE_REBOOT_MSG = "Reboot {} node..."
    RESTORE_REMAIN_POOL = "Restore remain pool..."
    RESTORE_FINISH_MSG = "Restore Finish..."

    """
    ----------------------------------------------------------
    Config Constants
    ----------------------------------------------------------
    """
    CONFIGURE_MENU = [
        ("1", "Add Node"),
        ("2", "Remove Node")
    ]
    ADD_NODE_INFO = [
        ("Node Name",   1, 5, "", 1, 20, 18, 30),
        ("IP Address",  2, 5, "", 2, 20, 18, 30),
        ("Description", 3, 5, "", 3, 20, 18, 30)
    ]
    DELETE_CHECK_MSG = "Are you sure you want to permanently {} node remove?"