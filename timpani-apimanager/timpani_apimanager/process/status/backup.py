from enum import Enum, unique

@unique
class BackupStatus(Enum):
    # Backup Process Name
    PROC_BACKUP = 'BackupProc'

    # Backup Kind Code
    KIND_ORIGINAL = 'original'
    KIND_ROOT = 'root'
    KIND_USER = 'user'

    # Backup Processing Code
    ZVOLMETADATAGET = ('zvolmetadataget', 'get zvol meta data')
    ZVOLMETADATACOLLECT = ('zvolmetadatacollect', 'zvol meta data collection')
    INCREMENTPOLICE = ('incrementpolice', 'POLICE')
    NFSMOUNT = ('nfsmount', 'Data Storage Mount')
    SNAPSHOTCREATE = ('snapshotcreate', 'Snapshot Create')
    SNAPSHOTMETADATACOLLECT = ('snapshotmetadatacollect', 'Snapshot meta data collection')
    SNAPSHOTDESTROY = ('snapshotdestroy', 'Snapshot Destroy')
    METADATAUPDATE = ('metadataupdate', 'Meta data update')
    NFSUNMOUNT = ('nfsunmount', 'Data Storage Unmount')
    SNAPSHOTCREATE_FULL = ('snapshotcreatefull', 'Snapshot Create')
    SNAPSHOTDESTROY_FULL = ('snapshotdestroyfull', 'Snapshot Destroy')
    RSYNCOSBACKUP = ('rsyncosbackup', 'Snapshot Create')
    RSYNCDATABACKUP = ('rsyncdatabackup', 'Snapshot Create')
    RSYNCGETDATA = ('rsyncgetdata', 'get meta data')
    RSYNCMETACOLLECT = ('rsyncmetacollect', 'meta data collect')
    RSYNCMETADATAUPDATE = ('rsyncmetadataupdate', 'Meta data update')

    PROC_ALL_LIST = [ZVOLMETADATAGET, ZVOLMETADATACOLLECT, INCREMENTPOLICE, SNAPSHOTDESTROY, SNAPSHOTCREATE,
                     SNAPSHOTMETADATACOLLECT, NFSMOUNT, NFSUNMOUNT, METADATAUPDATE, RSYNCOSBACKUP,
                     RSYNCDATABACKUP, RSYNCGETDATA, RSYNCMETACOLLECT, RSYNCMETADATAUPDATE, SNAPSHOTCREATE_FULL,
                     SNAPSHOTDESTROY_FULL
                     ]

    PROC_INCREMENT_FREEBSD = [ZVOLMETADATAGET[0],
                              INCREMENTPOLICE[0],
                              NFSMOUNT[0],
                              ZVOLMETADATACOLLECT[0],
                              SNAPSHOTCREATE[0],
                              SNAPSHOTMETADATACOLLECT[0],
                              SNAPSHOTDESTROY[0],
                              METADATAUPDATE[0],
                              NFSUNMOUNT[0]
                              ]

    PROC_FULL_FREEBSD = [ZVOLMETADATAGET[0],
                         NFSMOUNT[0],
                         ZVOLMETADATACOLLECT[0],
                         SNAPSHOTCREATE_FULL[0],
                         SNAPSHOTMETADATACOLLECT[0],
                         SNAPSHOTDESTROY_FULL[0],
                         METADATAUPDATE[0],
                         NFSUNMOUNT[0]
                        ]

    PROC_RSYNC_FULL = [RSYNCGETDATA[0],
                       RSYNCMETACOLLECT[0],
                       NFSMOUNT[0],
                       RSYNCOSBACKUP[0],
                       RSYNCMETADATAUPDATE[0],
                       NFSUNMOUNT[0]
                       ]

    PROC_RSYNC_DATA = [RSYNCGETDATA[0],
                       RSYNCMETACOLLECT[0],
                       NFSMOUNT[0],
                       RSYNCDATABACKUP[0],
                       RSYNCMETADATAUPDATE[0],
                       NFSUNMOUNT[0]
                       ]


