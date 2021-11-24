from enum import Enum, unique

@unique
class DeleteProc(Enum):
    # Backup Process Name
    PROC_BIOS = 'DeleteProc'

    FILECHECK = ('filecheck', 'Target Directory Check')
    SNAPDIRDELETE = ('snapdirdelete', 'Snap File Directory Delete')
    PARTDIRDELETE = ('partdirdelete', 'Partition Information Delete')
    UPDATEDELETEDATA = ('updatesnapdel', 'Snap Delete Info Update')

    PROC_ALL_LIST = [ FILECHECK, SNAPDIRDELETE, PARTDIRDELETE, UPDATEDELETEDATA
                    ]

    PROC_SNAP = [FILECHECK[0],
                 SNAPDIRDELETE[0],
                 PARTDIRDELETE[0],
                 UPDATEDELETEDATA[0]
                 ]