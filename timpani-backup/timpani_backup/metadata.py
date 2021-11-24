import logging
import platform
from timpani_backup.resource import ResourceSystem

logger = logging.getLogger(__name__)

class BackupMetaData(object):

    @staticmethod
    def metadatacollection():
        res_data = {}
        # partition information collecation

        # zpool property collection
        zpool_property = ResourceSystem.getZpoolGetAll()

        # zfs property collection
        zfs_property = ResourceSystem.getZfsGetAll()

        # zfs list -Hv
        if platform.system() == 'FreeBSD':
            zpool_status = ResourceSystem.zpoollistHv()
        else:
            zpool_status = ResourceSystem.zpoollistHv(True)
        # print(zpool_status)

        # geom list

        if platform.system() == 'FreeBSD':
            geom_list = ResourceSystem.geomlist()
        else:
            geom_list = None

        zdb_list = ResourceSystem.zdb_list()

        res_data = {'zpool_property': zpool_property, 'zfs_property': zfs_property,
                    'zdb_list': zdb_list, 'geom_list': geom_list, 'zpool_status': zpool_status }
        return res_data
