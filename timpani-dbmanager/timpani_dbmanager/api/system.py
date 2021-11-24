import logging
from timpani_dbmanager.db import dao
from .base import Base
from timpani_dbmanager.db.dao.base_dao import BaseDAO

import uuid

logger = logging.getLogger(__name__)

class SystemAPI(object):
    base = Base()

    @BaseDAO.database_operation
    def registerAgent(self, data, database_session):
        logger.info('registerAgent {}'.format(data))
        res_data = {}
        agent_uuid = dao.system_dao.AgentDAO.register_agent(data, database_session=database_session)
        res_data['agent_id'] = agent_uuid
        return res_data

    @BaseDAO.database_operation
    def registerSystemInfo(self, data, database_session):
        """
        Create tb_system Table
        :param data:
        :param database_session:
        :return:
        """
        logger.info('registerSystemInfo {}'.format(data))
        res_data = {}
        system_id = dao.system_dao.systemDAO.getSystemID(data, database_session=database_session)

        if system_id is None:
            if data.get('os_type').upper().__eq__('LINUX'):
                data['os_type_code'] = 'TO01'
            else:
                data['os_type_code'] = 'TO02'
            if data.get('os_arch').upper().__eq__('X86_64'):
                data['os_arch_code'] = 'AO01'
            else:
                data['os_arch_code'] = 'AO02'
            system_id, node_uuid = dao.system_dao.systemDAO.registerSystem(data, database_session=database_session)
            node_data = {}
            node_data['system_id'] = system_id
            node_data['nodeuuid'] = node_uuid
            node_uuid = dao.node_dao.NodeDAO.update_node(node_data, database_session=database_session)
            if node_uuid is None:
                logging.warning("Not Found Node Register Information")
            else:
                logging.info("node_uuid : {}".format(node_uuid))
        else:
            logger.warning('Exist System ID : node_uuid : {}'.format(data.get('node_uuid')))

        res_data['system_id'] = system_id
        return res_data

    @BaseDAO.database_operation
    def SetBackupSrc(self, data, database_session):
        logger.info('SetBackupSrc {}'.format(data))
        res_data = {}
        node_uuid = data.get('node_uuid')
        backup_src_data = data.get('result')
        current_time = dao.system_dao.SystemZfsDAO.GetNowTime()
        system_id = dao.system_dao.systemDAO.getSystemID(data, database_session=database_session)
        for src_data in backup_src_data:
            if src_data.get('zfs_type').__eq__('filesystem'):
                src_data['zfs_type_code'] = 0
            elif src_data.get('zfs_type').__eq__('volume'):
                src_data['zfs_type_code'] = 1
            else:
                src_data['zfs_type_code'] = 3
            src_data['register_dt'] = current_time
            src_data['node_uuid'] = node_uuid
            if system_id is not None:
                src_data['system_id'] = system_id
            dao.system_dao.SystemZfsDAO.SetBackupSrc(src_data, database_session=database_session)
        notmatch_data = {'node_uuid': node_uuid, 'register_dt': current_time}
        dao.system_dao.SystemZfsDAO.DelBackupSrcNotMatch(notmatch_data, database_session=database_session)

        return {'status': 'Success'}

    @BaseDAO.database_operation
    def GetBackupSrc(self, data, database_session):
        logger.info('GetBackupSrc {}'.format(data))
        res_query = dao.system_dao.SystemZfsDAO.GetBackupSrc(data, database_session=database_session)
        logger.info('Res Query : {}'.format(res_query))
        return res_query

    @BaseDAO.database_operation
    def GetRecoverSrc(self, data, database_session):
        logger.info('GetRecoverSrc {}'.format(data))
        res_query = dao.system_dao.SystemBakupImageDAO.getrecoverlist(data, database_session=database_session)
        logger.info('Res Query : {}'.format(res_query))
        return res_query

    @BaseDAO.database_operation
    def GetSystemHistory(self, data, database_session):
        logger.info('GetSystemHistory {}'.format(data))
        res_query = dao.system_dao.SystemZfsDAO.GetSystemHistory(data, database_session=database_session)
        logger.info('Res Query : {}'.format(res_query))
        return res_query

    @BaseDAO.database_operation
    def GetSystemProcessHistory(self, data, database_session):
        logger.info('GetSystemProcessHistory {}'.format(data))
        target_type_list = data.get('target_type_list')
        query_equl = False
        res = None
        res_error = None
        res_query = None
        if 'target_type_list' in data:
            for target_type in target_type_list:
                if target_type.__eq__('error'):
                    res_error = dao.system_dao.SystemProcessStatusErrHistDAO.get_process_hist_err(data, database_session=database_session)
                else:
                    if not query_equl:
                        res_query = dao.system_dao.SystemProcessStatusHistDAO.get_process_hist(data, database_session=database_session)
                        query_equl = True

        if res_query is not None:
            res = res_query

        if res is None:
            res = []

        if res_error is not None:
            logger.info('Res Query ERROR : {}'.format(res_error))
            for error_data in res_error:
                res.append(error_data)
        logger.info('Res Query : {}'.format(res))
        return res

    @BaseDAO.database_operation
    def backupmetadata(self, data, database_session):
        logger.info('backupmetadata {}'.format(data))
        res_data = {}
        node_uuid = data.get('node_uuid')
        system_id = dao.system_dao.systemDAO.getSystemID(data, database_session=database_session)
        data['system_id'] = system_id
        if data['backup_kind'].__eq__('full'):
            data['backup_kind_code'] = 'BKF'
        else:
            data['backup_kind_code'] = 'BKI'
        meta_id = dao.system_dao.SystemBackupMetaDAO.register_systembackupmeta(data, database_session=database_session)
        meta_data = data.get('result')
        zpool_property_data_list = meta_data.get('zpool_property')
        zfs_property_data_list = meta_data.get('zfs_property')
        zdb_list_data = meta_data.get('zdb_list')

        for zpool_property in zpool_property_data_list:
            zpool_property['node_uuid'] = node_uuid
            zpool_property['meta_id'] = meta_id
            dao.system_dao.SystemZpoolPropertyDAO.register_zpool_property(zpool_property, database_session=database_session)

        for zfs_property in zfs_property_data_list:
            zfs_property['node_uuid'] = node_uuid
            zfs_property['meta_id'] = meta_id
            dao.system_dao.SystemZfsPropertyDAO.register_zfs_property(zfs_property, database_session=database_session)

        if 'geom_list' in meta_data:
            geom_list = meta_data.get('geom_list')
            if geom_list is not None:
                if len(geom_list) > 0:
                    for geom in geom_list:
                        geom['meta_id'] = meta_id
                        dao.system_dao.SystemGeomListDAO.register_geom_list(geom, database_session=database_session)

        if 'zpool_status' in meta_data:
            zpool_status_list = meta_data.get('zpool_status')
            logger.info(zpool_status_list)
            if zpool_status_list is not None:
                if len(zpool_status_list) > 0:
                    for zpool_status in zpool_status_list:
                        pool = zpool_status.get('pool')
                        raid_info = zpool_status.get('raid')
                        device_list = raid_info.get('device_list')
                        for device in device_list:
                            zpool_data = {
                                'meta_id': meta_id,
                                'pool': pool,
                                'method': raid_info.get('method'),
                                'create_cnt': raid_info.get('create_cnt'),
                                'device': device
                            }
                            dao.system_dao.SystemZpoolListHvDAO.register_zpool_list_hv(zpool_data, database_session=database_session)

        if 'snapshot_list' in meta_data:
            snapshot_list = meta_data.get('snapshot_list')
            if snapshot_list is not None:
                for snapshot_data in snapshot_list:
                    snapshot_data['meta_id'] = meta_id
                    snapshot_list_id = dao.system_snap_dao.systemSnapDAO.registerSystemSnapList(snapshot_data, database_session=database_session)

        if 'image_list' in meta_data:
            image_list = meta_data.get('image_list')
            if image_list is not None:
                for backup_image in image_list:
                    backup_image['meta_id'] = meta_id
                    child_id = dao.system_dao.SystemBakupImageDAO.register_systembackupimage(backup_image, database_session=database_session)
                    backup_image['child_id'] = child_id
                    parent_id = dao.system_dao.SystemBakupImageDAO.update_parent_id(backup_image, database_session=database_session)

        if 'gpart_backup_list' in meta_data:
            gpart_backup_list = meta_data.get('gpart_backup_list')
            if gpart_backup_list is not None:
                logger.info('================= 5')
                for gpart_backup in gpart_backup_list:
                    gpart_backup['meta_id'] = meta_id
                    dao.system_dao.SystemGpartBackupDAO.register_gpart_backup(gpart_backup, database_session=database_session)

        for zdb_data in zdb_list_data:
            pool_info = zdb_data.get('pool_info')
            pool_info['meta_id'] = meta_id
            vdev_tree_uuid = dao.system_dao.SystemMetaZpoolDAO.register_meta_zpool(pool_info, database_session=database_session)
            logger.info('vdev_tree_uuid : {}'.format(vdev_tree_uuid))
            vdev_tree = pool_info.get('vdev_tree')
            vdev_tree['vdev_tree_uuid'] = vdev_tree_uuid
            vdev_tree['meta_id'] = meta_id
            dao.system_dao.SystemMetaVdevTreeDAO.register_meta_vdevtree(vdev_tree, database_session=database_session)
            children_list = vdev_tree.get('children')
            logger.info('================= 6')
            for children in children_list:
                logger.info(children)
                children['meta_id'] = meta_id
                children['vdev_tree_uuid'] = vdev_tree_uuid
                children['children_id'] = children['id']
                children['is_children_sub'] = '0'
                if 'children_sub' in children:
                    if len(children['children_sub']) > 1:
                        children['is_children_sub'] = '1'
                children_sub_uuid = dao.system_dao.SystemMetaChildrenDAO.register_meta_children(children, database_session=database_session)
                logger.info('================= 7')
                if 'children_sub' in children:
                    children_sub_list = children['children_sub']
                    if len(children_sub_list) > 0:
                        for children_sub in children_sub_list:
                            children_sub['meta_id'] = meta_id
                            children_sub['vdev_tree_uuid'] = vdev_tree_uuid
                            children_sub['children_sub_uuid'] = children_sub_uuid
                            children_sub['children_sub_id'] = children_sub['id']
                            dao.system_dao.SystemBackupChildrenSubDAO.register_meta_children_sub(children_sub, database_session=database_session)

        return '1'

    @BaseDAO.database_operation
    def backupmetadata_linux(self, data, database_session):
        logger.info('backupmetadata {}'.format(data))
        res_data = {}
        node_uuid = data.get('node_uuid')
        system_id = dao.system_dao.systemDAO.getSystemID(data, database_session=database_session)
        data['system_id'] = system_id
        if data['backup_kind'].__eq__('full'):
            data['backup_kind_code'] = 'BKF'
        else:
            data['backup_kind_code'] = 'BKI'
        meta_id = dao.system_dao.SystemBackupMetaDAO.register_systembackupmeta(data, database_session=database_session)
        meta_data = data.get('result')

        part_list = meta_data.get('part')
        snap_list = meta_data.get('snap')
        for snap in snap_list:
            image_data = snap.get('image')
            rsync_data = snap.get('rsync')
            # snap image save
            image_data['meta_id'] = meta_id
            child_id = dao.system_dao.SystemBakupImageDAO.register_systembackupimage(image_data,
                                                                                     database_session=database_session)
            # rsync data save
            rsync_data['meta_id'] = meta_id
            dao.system_snap_dao.SystemLinuxRsyncDAO.registerLinuxRsync(rsync_data, database_session=database_session)

        for part in part_list:
            part['meta_id'] = meta_id
            dao.system_snap_dao.SystemLinuxPartDAO.registerLinuxPart(part, database_session=database_session)

        return '1'

    @BaseDAO.database_operation
    def processhistory(self, data, database_session):
        logger.info('processhistory {}'.format(data))
        res_data = {}
        # node_uuid = data.get('node_uuid')
        run_status = data.get('action_status')

        if run_status.__eq__('START'):
            logger.info('run_status RUN')
            run_uuid = dao.system_dao.SystemProcessStatusDAO.start_process(data, database_session=database_session)
        elif run_status.__eq__('END'):
            logger.info('run_status END')
            dao.system_dao.SystemProcessStatusDAO.update_process(data, database_session=database_session)
            # result = dao.system_dao.SystemProcessStatusDAO.end_process(data, database_session=database_session)
            run_uuid = None
        elif run_status.__eq__('ERROR'):
            logger.info('run_status ERROR')
            dao.system_dao.SystemProcessStatusDAO.update_process(data, database_session=database_session)
            dao.system_dao.SystemProcessStatusErrHistDAO.register_process_hist_err(data, database_session=database_session)
            # result = dao.system_dao.SystemProcessStatusDAO.end_process(data, database_session=database_session)
            run_uuid = None
        else:
            logger.info('run_status PASS')
            run_uuid = dao.system_dao.SystemProcessStatusDAO.update_process(data, database_session=database_session)

        dao.system_dao.SystemProcessStatusHistDAO.register_process_hist(data, database_session=database_session)

        return {'run_uuid': run_uuid}

    @BaseDAO.database_operation
    def getprocesshistory(self, data, database_session):
        logger.info('getprocesshistory {}'.format(data))
        res = dao.system_dao.SystemProcessStatusDAO.gethistory(data, database_session)
        return res

    @BaseDAO.database_operation
    def getreallog(self, data, database_session):
        logger.info('getreallog {}'.format(data))
        res = dao.system_dao.SystemProcessStatusHistDAO.getrealhist(data, database_session)
        if res is None:
            res = []

        res_error = dao.system_dao.SystemProcessStatusErrHistDAO.getrealhist(data, database_session)
        for error_data in res_error:
            res.append(error_data)
        return res

    @BaseDAO.database_operation
    def checkprocessstatus(self, data, database_session):
        logger.info('checkprocessstatus {}'.format(data))
        res_data = {}
        node_uuid = data.get('node_uuid')
        status = dao.system_dao.SystemProcessStatusDAO.get_status(data, database_session=database_session)
        return {'status': status}

    @BaseDAO.database_operation
    def getsysteminfo(self, data, database_session):
        res = dao.system_dao.systemDAO.getsysteminfo(data=data, database_session=database_session)
        return res

########################################## RECOVER ####################################################

    @BaseDAO.database_operation
    def getnodeuuid_image(self, data, database_session):
        logger.debug('getnodeuuid_image {}'.formate(data))
        res_data = {}

    @BaseDAO.database_operation
    def get_snapshotlist(self, data, database_session):
        logger.debug('get_snapshotlist {}'.format(data))
        res_query = dao.system_dao.SystemBakupImageDAO.getMeta_ID(data, database_session=database_session)
        logger.info('Get Meta ID Res Query : {}'.format(res_query))
        data['meta_id'] = res_query.get('meta_id')
        res_query = dao.system_snap_dao.systemSnapDAO.get_systemSnapList(data, database_session=database_session)
        logger.info('Res Query : {}'.format(res_query))
        return res_query

    @BaseDAO.database_operation
    def get_snapshotImageList(self, data, database_session):
        logger.debug('get_snapshotImageList find list : {}'.format(data['snapshot_find_list']))
        res_query = dao.system_dao.SystemBakupImageDAO.getSnapshotImageList(data, database_session=database_session)
        return res_query

    @BaseDAO.database_operation
    def get_TargetImageList(self, data, database_session):
        logger.debug('get_TargetImageList find list : {}'.format(data['target_image']))
        res_query = dao.system_dao.SystemBakupImageDAO.getTargetImageList(data, database_session=database_session)
        return res_query

    @BaseDAO.database_operation
    def get_RsyncBaseData(self, data, database_session):
        logger.debug('get_RsyncBaseData : {}'.format(data))
        res_query = dao.system_snap_dao.SystemLinuxRsyncDAO.get_LinuxRsync(data, database_session=database_session)
        return res_query








