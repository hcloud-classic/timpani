from enum import Enum, unique

@unique
class RestoreStatus(Enum):
    # Backup Process Name
    PROC_RESTORE = 'RestoreProc'

    # Restore Processing Code
    ZVOLMETADATAGET = ('zvolmetadataget', 'zvol meta data')
    ZVOLMETADATACOLLECT = ('zvolmetadatacollect', 'zvol meta data collection')
    METADATACOMPARE = ('metadatacompare', 'compare current meta data and priv meta data')
    ISCSIDEMONCHECK = ('iscsidemoncheck', 'iscsi demon check')
    ISCSIREQUNMOUNT = ('iscsirequnmount', 'iscsi unmount request')
    ISCSIREQMOUNT = ('iscsireqmount', 'iscsi mount request')
    ISCSILUNINFODEL = ('iscsiluninfodel', 'iscsi LUN info delete')
    ISCSILUNINFOADD = ('iscsiluninfoadd', 'iscsi LUN info restore')
    DATASETRENAME = ('datasetrename', 'target dataset rename')
    RENAMEDATADEL = ('renamedatadel', 'target rename dataset delete')
    SNAPSHOTRESTORE = ('snapshotrestore', 'snapshot restore')
    SNAPSHOTRESTORE_FULL = ('snapshotrestorefull', 'snapshot restore')
    RSYNCOSRESTORE = ('rsyncosrestore', 'data restore')
    RSYNCDATARESTORE = ('rsyncdatarestore', 'data restore')
    RSYNCPRIVDATACOLLECT = ('rsyncprivdatacollect', 'get snapshot data')

    NFSMOUNT = ('nfsmount', 'Data Storage Mount')
    METADATAUPDATE = ('metadataupdate', 'Meta data update')
    METADATAUPDATE_OS = ('metadataupdateos', 'Meta data update')
    NFSUNMOUNT = ('nfsunmount', 'Data Storage Unmount')

    PROC_ALL_LIST = [ZVOLMETADATAGET, ZVOLMETADATACOLLECT, METADATACOMPARE, ISCSIDEMONCHECK,
                     ISCSIREQUNMOUNT, ISCSIREQMOUNT, ISCSILUNINFODEL, ISCSILUNINFOADD,
                     DATASETRENAME, RENAMEDATADEL, SNAPSHOTRESTORE, NFSMOUNT,
                     METADATAUPDATE, METADATAUPDATE_OS, SNAPSHOTRESTORE_FULL, RSYNCOSRESTORE,
                     RSYNCDATARESTORE, NFSUNMOUNT, RSYNCPRIVDATACOLLECT
                     ]

    PROC_INCREMENT_FREEBSD = [NFSMOUNT[0],
                              ZVOLMETADATACOLLECT[0],
                              METADATACOMPARE[0],
                              ISCSIDEMONCHECK[0],
                              ISCSIREQUNMOUNT[0],
                              ISCSILUNINFODEL[0],
                              DATASETRENAME[0],
                              SNAPSHOTRESTORE[0],
                              RENAMEDATADEL[0],
                              ISCSILUNINFOADD[0],
                              ISCSIREQMOUNT[0],
                              NFSUNMOUNT[0],
                              METADATAUPDATE[0]
                              ]

    PROC_FULL_FREEBSD = [NFSMOUNT[0],
                              ZVOLMETADATACOLLECT[0],
                              METADATACOMPARE[0],
                              ISCSIDEMONCHECK[0],
                              ISCSIREQUNMOUNT[0],
                              ISCSILUNINFODEL[0],
                              DATASETRENAME[0],
                              SNAPSHOTRESTORE_FULL[0],
                              RENAMEDATADEL[0],
                              ISCSILUNINFOADD[0],
                              ISCSIREQMOUNT[0],
                              NFSUNMOUNT[0],
                              METADATAUPDATE_OS[0]
                              ]

    PROC_RSYNC_OS = [RSYNCPRIVDATACOLLECT[0],
                     NFSMOUNT[0],
                     RSYNCOSRESTORE[0],
                     NFSUNMOUNT[0],
                     METADATAUPDATE_OS[0]
                    ]

    PROC_RSYNC_DATA = [RSYNCPRIVDATACOLLECT[0],
                       NFSMOUNT[0],
                       RSYNCDATARESTORE[0],
                       NFSUNMOUNT[0],
                       METADATAUPDATE[0]
                       ]

