import logging
from .base_dao import BaseDAO

from ..models.system import (SystemBackupSnapshotList, SystemLinuxRsyncBackup, SystemLinuxPartBackup
                             )
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

class systemSnapDAO(BaseDAO):

    @staticmethod
    def registerSystemSnapList(data, database_session):
        obj = SystemBackupSnapshotList()
        meta_id = data.get('meta_id')
        if meta_id is None:
            data['meta_id'] = None

        if isinstance(data.get('index_id'), str):
            data['index'] = int(data.get('index_id'))
        else :
            data['index'] = data.get('index_id')

        field_list = ["meta_id", "index", "start_dataset", "dataset", "snapname", "snapshot_name",
                      "create_time"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod  # @BaseDAO.database_operation
    def update_systemSnapList(data, database_session):
        obj = database_session.query(SystemBackupSnapshotList).filter(
            SystemBackupSnapshotList.meta_id == data.get('meta_id')).first()
        field_list = ["meta_id", "index", "start_dataset", "dataset", "snapname", "snapshot_name",
                      "create_time"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.id

    @staticmethod  # @BaseDAO.database_operation
    def get_systemSnapList(data, database_session):

        query = database_session.query(SystemBackupSnapshotList.id,
                                       SystemBackupSnapshotList.meta_id,
                                       SystemBackupSnapshotList.index,
                                       SystemBackupSnapshotList.start_dataset,
                                       SystemBackupSnapshotList.dataset,
                                       SystemBackupSnapshotList.snapname,
                                       SystemBackupSnapshotList.snapshot_name,
                                       SystemBackupSnapshotList.create_time,
                                       SystemBackupSnapshotList.register_dt)

        if 'meta_id' in data:
            query = query.filter(SystemBackupSnapshotList.meta_id == data.get('meta_id')).all()
        else:
            query = query.filter(SystemBackupSnapshotList.snapname == data.get('snapname')).first()

        field_list = ['id', 'meta_id', 'index', 'start_dataset',
                      'dataset', 'snapname', 'snapshot_name', 'create_time', 'register_dt']
        res = BaseDAO.return_data(query=query, field_list=field_list)

        return res

    @staticmethod  # @BaseDAO.database_operation
    def del_systemSnapList(data, database_session):
        try:
            data = database_session.query(SystemBackupSnapshotList).filter(
                SystemBackupSnapshotList.meta_id == data.get('meta_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'

class SystemLinuxRsyncDAO(BaseDAO):

    @staticmethod
    def registerLinuxRsync(data, database_session):
        obj = SystemLinuxRsyncBackup()
        meta_id = data.get('meta_id')
        if meta_id is None:
            data['meta_id'] = None

        field_list = ["meta_id", "target", "snap_name", "snap_target", "ref_path",
                      "parent_ref_path", "home_path", "backup_date"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod  # @BaseDAO.database_operation
    def get_LinuxRsync(data, database_session):

        query = database_session.query(SystemLinuxRsyncBackup.id,
                                       SystemLinuxRsyncBackup.meta_id,
                                       SystemLinuxRsyncBackup.target,
                                       SystemLinuxRsyncBackup.snap_name,
                                       SystemLinuxRsyncBackup.snap_target,
                                       SystemLinuxRsyncBackup.ref_path,
                                       SystemLinuxRsyncBackup.parent_ref_path,
                                       SystemLinuxRsyncBackup.home_path,
                                       SystemLinuxRsyncBackup.backup_date,
                                       SystemLinuxRsyncBackup.register_dt
                                       )

        if 'meta_id' in data:
            query = query.filter(SystemLinuxRsyncBackup.meta_id == data.get('meta_id')).all()
        else:
            query = query.filter(SystemLinuxRsyncBackup.snap_name == data.get('snapname')).\
                filter(SystemLinuxRsyncBackup.target == data.get('dataset'))
        BaseDAO.debug_sql_print(query,'get_LinuxRsync')
        query = query.first()

        field_list = ['id', 'meta_id', 'target', 'snap_name',
                      'snap_target', 'ref_path', 'parent_ref_path', 'home_path', 'backup_date', 'register_dt']
        res = BaseDAO.return_data(query=query, field_list=field_list)

        return res

    @staticmethod  # @BaseDAO.database_operation
    def del_LinuxRsync(data, database_session):
        try:
            data = database_session.query(SystemLinuxRsyncBackup).filter(
                SystemLinuxRsyncBackup.meta_id == data.get('meta_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'


class SystemLinuxPartDAO(BaseDAO):
    @staticmethod
    def registerLinuxPart(data, database_session):
        obj = SystemLinuxPartBackup()
        meta_id = data.get('meta_id')
        if meta_id is None:
            data['meta_id'] = None

        field_list = ["meta_id", "mountpoint", "subsystems", "type", "file_part_path", "name", "tran",
                      "uuid", "fstype", "label", "kname"
                      ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod  # @BaseDAO.database_operation
    def get_LinuxPart(data, database_session):

        query = database_session.query(SystemLinuxPartBackup.id,
                                       SystemLinuxPartBackup.meta_id,
                                       SystemLinuxPartBackup.mountpoint,
                                       SystemLinuxPartBackup.subsystems,
                                       SystemLinuxPartBackup.type,
                                       SystemLinuxPartBackup.file_part_path,
                                       SystemLinuxPartBackup.name,
                                       SystemLinuxPartBackup.tran,
                                       SystemLinuxPartBackup.uuid,
                                       SystemLinuxPartBackup.fstype,
                                       SystemLinuxPartBackup.label,
                                       SystemLinuxPartBackup.kname,
                                       SystemLinuxPartBackup.register_dt
                                       )

        query = query.filter(SystemLinuxPartBackup.meta_id == data.get('meta_id')).all()

        field_list = ["meta_id", "mountpoint", "subsystems", "type", "file_part_path", "name", "tran",
                      "uuid", "fstype", "label", "kname",
                      "register_dt"]
        res = BaseDAO.return_data(query=query, field_list=field_list)

        return res

    @staticmethod  # @BaseDAO.database_operation
    def del_LinuxPart(data, database_session):
        try:
            data = database_session.query(SystemLinuxPartBackup).filter(
                SystemLinuxPartBackup.meta_id == data.get('meta_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'
