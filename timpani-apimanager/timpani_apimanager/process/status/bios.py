from enum import Enum, unique

@unique
class BiosProc(Enum):
    # Backup Process Name
    PROC_BIOS = 'BiosProc'

    IPMICHECK = ('ipmicheck', 'ipmi communication check') #all
    TEMPLATEDEPLOY = ('ipmipoweroff', 'target power off and template deploy')
    IPMIPOWERON = ('ipmipoweron', 'target power on')
    IPMIPOWERSTATUS = ('ipmipowerstatus', 'ipmi power status check')
    SYSCFGPATCH = ('syscfgpatch', 'template syscfg make') #set
    SYSCFGDUMP = ('syscfgdump', 'bios config dump')
    SYSCFGBACKUP = ('syscfgbackup', 'backup syscfg')
    REQISCSIOFF = ('reqiscsioff', 'request iscsi off')
    CHECKBIOSVALUE = ('checkbiosvalue', 'check bios value check')
    UPDATEBIOSDATA = ('updatebiosdata', 'current bios value update')
    BIOSDATACOLLECT = ('biosdatacollect', 'bios data collect')
    NFSMOUNT = ('nfsmount', 'Data Storage Mount')
    NFSUNMOUNT = ('nfsunmount', 'Data Storage Unmount')
    GETCURBIOSCONFIG = ('getcurbiosconfig', 'current bios config get data')

    PROC_ALL_LIST = [ IPMICHECK, TEMPLATEDEPLOY, IPMIPOWERON, IPMIPOWERSTATUS,
                      SYSCFGPATCH, SYSCFGDUMP, SYSCFGBACKUP, REQISCSIOFF,
                      CHECKBIOSVALUE, UPDATEBIOSDATA, BIOSDATACOLLECT, NFSMOUNT, NFSUNMOUNT,
                      GETCURBIOSCONFIG]

    PROC_DUMP = [GETCURBIOSCONFIG[0],
                 IPMICHECK[0],
                 IPMIPOWERSTATUS[0],
                 REQISCSIOFF[0],
                 SYSCFGDUMP[0],
                 NFSMOUNT[0],
                 SYSCFGBACKUP[0],
                 BIOSDATACOLLECT[0],
                 NFSUNMOUNT[0],
                 UPDATEBIOSDATA[0]
                 ]

    PROC_SET = [GETCURBIOSCONFIG[0],
                IPMICHECK[0],
                IPMIPOWERSTATUS[0],
                REQISCSIOFF[0],
                NFSMOUNT[0],
                SYSCFGPATCH[0],
                TEMPLATEDEPLOY[0],
                CHECKBIOSVALUE[0],
                BIOSDATACOLLECT[0],
                NFSUNMOUNT[0],
                UPDATEBIOSDATA[0]
                ]
