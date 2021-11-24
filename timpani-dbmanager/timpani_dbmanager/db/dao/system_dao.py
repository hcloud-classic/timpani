import logging
from .base_dao import BaseDAO

from ..models.system import (System, SystemBackupImage, SystemBackupMeta, SystemDisk,
                             SystemHist, SystemZfs, Agent, SystemPropertyZpool, SystemPropertyZfs,
                             SystemBackupMetaVdevTree, SystemBackupMetaZpool,
                             SystemBackupMetaChildren, SystemBackupMetaChildrenSub,
                             SystemZpoolListHv, SystemGpartBackup, SystemGeomList,
                             SystemProcessStatus, SystemProcessStatusHist,
                             SystemProcessStatusErrHist
                             )
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

class agentDAO(BaseDAO):

    @staticmethod
    def registerAgent(data, database_session):
        obj = Agent()
        field_list = ["capability", "capability_code", "ipv4address", "ipv4port", "node_uuid", "pid", "macaddress"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)
        res_id = obj.uuid
        return res_id


class systemDAO(BaseDAO):
    @staticmethod
    def getSystemID(data, database_session):
        query = database_session.query(System).filter(System.node_uuid == data.get('node_uuid')).first()
        if query is None:
            return None
        else:
            return query.id

    @staticmethod
    def registerSystem(data, database_session):
        obj = System()
        meta_id = data.get('meta_id')
        if meta_id is None:
            data['meta_id'] = None
        field_list = ["node_uuid", "meta_id", "ipv4address", "os_type", "os_type_code", "os_arch", "os_arch_code",
                      "kernel_version", "os_name", "os_version", "hostname"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def update_system(data, database_session):
        obj = database_session.query(System).filter(
            System.node_uuid == data.get('node_uuid')).first()
        field_list = ["node_uuid", "meta_id", "ipv4address", "os_type", "os_type_code", "os_arch", "os_arch_code",
                      "kernel_version", "os_name", "os_version", "hostname"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod
    def getsysteminfo(data, database_session):
        query = database_session.query(System.os_type, System.os_name, System.ipv4address).filter(
            System.node_uuid == data.get('node_uuid')). \
            first()

        field_list = ['os_type', 'os_name', 'ipaddress']
        res = BaseDAO.return_data(query=query, field_list=field_list)

        return res

    @staticmethod  # @BaseDAO.database_operation
    def del_system(data, database_session):
        try:
            data = database_session.query(System).filter(
                System.node_uuid == data.get('node_uuid')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'

class AgentDAO(BaseDAO):
    @staticmethod
    def register_agent(data, database_session):
        obj = Agent()
        field_list = ["capability", "capability_code", "ipv4address", "ipv4port", "node_uuid", "macaddress", "pid"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.uuid

    @staticmethod  # @BaseDAO.database_operation
    def update_agent(data, database_session):
        if 'node_uuid' in data:
            data['uuid'] = data.get('node_uuid')
        obj = database_session.query(Agent).filter(
            Agent.uuid == data.get('uuid')).first()
        field_list = ["uuid", "capability", "capability_code", "ipv4address", "macaddress", "pid", "ipv4port", "end_dt"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def del_agent(data, database_session):
        try:
            data = database_session.query(Agent).filter(Agent.uuid == data.get('uuid')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'

        return '1'


# class SystemZfs(Base):
#     __tablename__ = "tb_system_zfs"
#
#     id = Column(Integer, primary_key=True)
#     system_id = Column(Integer, ForeignKey('tb_system.id'))
#     zfs_used_size = Column(String(64))
#     zfs_avail_size = Column(String(64))
#     zfs_mount_point = Column(String(256))
#     zfs_name = Column(String(256))
#     register_dt = Column(DateTime(timezone=True), default=func.now())
#

class SystemZfsDAO(BaseDAO):

    @staticmethod
    def GetNowTime():
        return func.now()

    @staticmethod
    def SetBackupSrc(data, database_session):

        query = database_session.query(SystemZfs).filter(
                SystemZfs.node_uuid == data.get('node_uuid')).\
                filter(SystemZfs.zpool_name == data.get('zpool_name')).\
                filter(SystemZfs.zfs_name == data.get('zfs_name')).\
                first()

        field_list = ['node_uuid', 'zfs_used_size', 'zfs_avail_size', 'zfs_ref_size', 'zfs_type',
                      'zfs_type_code',  # 0:FileSystem, 1: Volume, 2: Snapshot
                      'zfs_mount_point', 'zfs_name', 'zpool_name', 'system_id'
                      ]

        if query is None:
            obj = SystemZfs()
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)
            res_id = obj.id
        else:
            BaseDAO.update_value(query, field_list, data)
            query.register_dt = data.get('register_dt')
            BaseDAO.update(query, database_session)
            res_id = query.id

        return res_id

    @staticmethod  # @BaseDAO.database_operation
    def GetBackupSrc(data, database_session):

        query = database_session.query(SystemZfs.zpool_name,
                                       SystemZfs.zfs_name,
                                       SystemZfs.zfs_type,
                                       SystemZfs.zfs_avail_size,
                                       SystemZfs.zfs_used_size,
                                       SystemZfs.zfs_ref_size,
                                       SystemZfs.zfs_mount_point,
                                       SystemZfs.register_dt).\
            filter(SystemZfs.node_uuid == data.get('node_uuid'))

        if 'zfs_type' in data:
            zfs_type_in = data.get('zfs_type')
            if isinstance(zfs_type_in, list):
                query = query.filter(SystemZfs.zfs_type.in_(zfs_type_in))

        query = query.all()
        field_list = ['zpool_name', 'zfs_name', 'zfs_type', 'zfs_avail_size',
                      'zfs_used_size', 'zfs_ref_size', 'zfs_mount_point', 'register_dt']
        res = BaseDAO.return_data(query=query, field_list=field_list)

        return res

    @staticmethod  # @BaseDAO.database_operation
    def DelBackupSrcNotMatch(data, database_session):

        try:
            obj_list = database_session.query(SystemZfs).filter(
                SystemZfs.node_uuid == data.get('node_uuid')).\
                filter(SystemZfs.register_dt < data.get('register_dt')).all()

            if isinstance(obj_list, list):
                for obj in obj_list:
                    BaseDAO.delete(obj, database_session)
            else:
                BaseDAO.delete(obj_list, database_session)
        except:
            return '0'
        return '1'

# class SystemDisk(Base):
#     __tablename__ = "tb_system_disk"
#
#     id = Column(Integer, primary_key=True)
#     system_id = Column(Integer, ForeignKey('tb_system.id'))
#     disk_used = Column(String(64))
#     disk_free = Column(String(64))
#     disk_avail = Column(String(64))
#     register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemDiskDAO(BaseDAO):
    @staticmethod
    def register_systemdisk(data, database_session):
        list = database_session.query(SystemDisk).filter(
            SystemDisk.system_id == data.get('system_id')).all()
        logger.info("list size : {} === {}".format(len(list), list))
        if len(list) != 0:
            return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = SystemDisk()
        field_list = ["system_id","disk_used","disk_free","disk_avail"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.system_id

    @staticmethod  # @BaseDAO.database_operation
    def update_systemdisk(data, database_session):
        obj = database_session.query(SystemDisk).filter(
            SystemDisk.system_id == data.get('system_id')).first()
        field_list = ["system_id", "disk_used", "disk_free", "disk_avail"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def del_systemdisk(data, database_session):
        try:
            data = database_session.query(SystemDisk).filter(
                System.system_id == data.get('system_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'
                
# class SystemBackupMeta(Base):
#     __tablename__ = "tb_system_backup_meta"
#
#     id = Column(Integer, primary_key=True)
#     system_id = Column(Integer, ForeignKey('tb_system.id'))
#     backup_kind = Column(String(32), nullable=False)
#     backup_kind_code = Column(String(32))
#     zfs_mount_point = Column(String(256))
#     image_name = Column(String(128))
#     zfs_name = Column(String(256))
#     zfs_used_size = Column(String(64))
#     zfs_avail_size = Column(String(64))
#     register_dt = Column(DateTime(timezone=True), default=func.now())
#     image_id = Column(Integer, ForeignKey('tb_system_backup_image.id'))
#     #image = relationship("SystemBackupImage", back_populates="meta")
#     #system = relationship("System", back_populates="backupmeta")

class SystemBackupMetaDAO(BaseDAO):

    @staticmethod
    def register_systembackupmeta(data, database_session):
        # list = database_session.query(SystemBackupMeta).filter(
        #     SystemBackupMeta.system_id == data.get('system_id')).first()
        # logger.info("list size : {} === {}".format(len(list), list))
        # if list is None:
        #     return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = SystemBackupMeta()
        field_list = ["system_id", "node_uuid", "backup_kind", "backup_kind_code"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def update_systembackupmeta(data, database_session):
        obj = database_session.query(SystemBackupMeta).filter(
            SystemBackupMeta.system_id == data.get('system_id')).first()
        field_list = ["zfs_property_id", "zpool_property_id", "zdb_id",
                      "image_id", "partition_id"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.system_id

    @staticmethod  # @BaseDAO.database_operation
    def del_systembackupmeta(data, database_session):
        try:
            data = database_session.query(SystemBackupMeta).filter(
                SystemBackupMeta.system_id == data.get('system_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'

class SystemBakupImageDAO(BaseDAO):
    @staticmethod
    def register_systembackupimage(data, database_session):

        obj = SystemBackupImage()
        field_list = ["meta_id", "image_kind", "image_kind_code", "image_hash", "image_name",
                      "image_size", "image_path", "parent_image_name", "zpool_name", "dataset"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def getnodeuuid_image(data, database_session):
        obj = database_session.query(SystemBackupImage.meta_id)

    @staticmethod
    def getrecoverlist(data, database_session):
        query = database_session.query(SystemBackupMeta.node_uuid,
                                       SystemBackupImage.zpool_name,
                                       SystemBackupImage.dataset,
                                       SystemBackupImage.image_kind,
                                       SystemBackupImage.image_name,
                                       SystemBackupImage.image_path,
                                       SystemBackupImage.image_size,
                                       SystemBackupImage.parent_id,
                                       SystemBackupImage.child_id,
                                       SystemBackupImage.parent_image_name,
                                       SystemBackupImage.register_dt). \
            join(SystemBackupMeta, SystemBackupMeta.id == SystemBackupImage.meta_id). \
            filter(SystemBackupMeta.node_uuid == data.get('node_uuid'))

        query = query.all()
        field_list = ['node_uuid', 'zpool_name', 'dataset', 'image_kind', 'image_name', 'image_path',
                      'image_size', 'parent_id', 'child_id', 'parent_image_name', 'register_dt']
        res = BaseDAO.return_data(query=query, field_list=field_list)

        return res

    @staticmethod
    def getMeta_ID(data, database_session):
        query = database_session.query(SystemBackupMeta.node_uuid,
                                       SystemBackupImage.meta_id,
                                       SystemBackupImage.zpool_name,
                                       SystemBackupImage.dataset,
                                       SystemBackupImage.image_kind,
                                       SystemBackupImage.image_name,
                                       SystemBackupImage.image_path,
                                       SystemBackupImage.image_size,
                                       SystemBackupImage.parent_id,
                                       SystemBackupImage.child_id,
                                       SystemBackupImage.parent_image_name,
                                       SystemBackupImage.register_dt). \
            join(SystemBackupMeta, SystemBackupMeta.id == SystemBackupImage.meta_id). \
            filter(SystemBackupMeta.node_uuid == data.get('node_uuid')). \
            filter(SystemBackupImage.image_name.in_(data.get('target_image')))


        query = query.first()
        field_list = ['node_uuid', 'meta_id', 'zpool_name', 'dataset', 'image_kind', 'image_name', 'image_path',
                      'image_size', 'parent_id', 'child_id', 'parent_image_name', 'register_dt']
        res = BaseDAO.return_data(query=query, field_list=field_list)

        return res

    @staticmethod
    def getSnapshotImageList(data, database_session):
        query = database_session.query(SystemBackupMeta.node_uuid,
                                       SystemBackupImage.meta_id,
                                       SystemBackupImage.zpool_name,
                                       SystemBackupImage.dataset,
                                       SystemBackupImage.image_kind,
                                       SystemBackupImage.image_name,
                                       SystemBackupImage.image_path,
                                       SystemBackupImage.image_size,
                                       SystemBackupImage.parent_id,
                                       SystemBackupImage.child_id,
                                       SystemBackupImage.parent_image_name,
                                       SystemBackupImage.register_dt). \
            join(SystemBackupMeta, SystemBackupMeta.id == SystemBackupImage.meta_id). \
            filter(SystemBackupMeta.node_uuid == data.get('node_uuid')). \
            filter(SystemBackupImage.image_name.in_(data.get('snapshot_find_list')))

        query = query.all()
        field_list = ['node_uuid', 'meta_id', 'zpool_name', 'dataset', 'image_kind', 'image_name', 'image_path',
                      'image_size', 'parent_id', 'child_id', 'parent_image_name', 'register_dt']
        res = BaseDAO.return_data(query=query, field_list=field_list)

        return res

    @staticmethod
    def getTargetImageList(data, database_session):
        query = database_session.query(SystemBackupMeta.node_uuid,
                                       SystemBackupImage.meta_id,
                                       SystemBackupImage.zpool_name,
                                       SystemBackupImage.dataset,
                                       SystemBackupImage.image_kind,
                                       SystemBackupImage.image_name,
                                       SystemBackupImage.image_path,
                                       SystemBackupImage.image_size,
                                       SystemBackupImage.parent_id,
                                       SystemBackupImage.child_id,
                                       SystemBackupImage.parent_image_name,
                                       SystemBackupImage.register_dt). \
            join(SystemBackupMeta, SystemBackupMeta.id == SystemBackupImage.meta_id). \
            filter(SystemBackupMeta.node_uuid == data.get('node_uuid')). \
            filter(SystemBackupImage.image_name.in_(data.get('target_image')))

        query = query.all()
        field_list = ['node_uuid', 'meta_id', 'zpool_name', 'dataset', 'image_kind', 'image_name', 'image_path',
                      'image_size', 'parent_id', 'child_id', 'parent_image_name', 'register_dt']
        res = BaseDAO.return_data(query=query, field_list=field_list)

        return res

    @staticmethod
    def update_parent_id(data, database_session):
        obj = database_session.query(SystemBackupImage).\
            filter(SystemBackupImage.image_name == data.get('parent_image_name')).first()

        if obj is None:
            return 0

        field_list = ['child_id']
        BaseDAO.update_value(obj, field_list, data)
        BaseDAO.update(obj, database_session)
        data['parent_id'] = obj.id

        obj1 = database_session.query(SystemBackupImage). \
            filter(SystemBackupImage.id == data.get('child_id')).first()
        field_list = ['parent_id']
        BaseDAO.update_value(obj1, field_list, data)
        BaseDAO.update(obj1, database_session)

        return obj.id


    @staticmethod  # @BaseDAO.database_operation
    def del_systembackupimage(data, database_session):
        try:
            obj_list = database_session.query(SystemBackupImage).filter(
                SystemBackupImage.meta_id == data.get('meta_id')).all()
            for obj in obj_list:
                BaseDAO.delete(obj, database_session)
        except:
            return '0'
        return '1'


class SystemHistDAO(BaseDAO):
    @staticmethod
    def register_systemhist(data, database_session):
        list = database_session.query(SystemHist).filter(
            SystemHist.node_uuid == data.get('node_uuid')).all()
        logger.info("list size : {} === {}".format(len(list), list))
        if len(list) != 0:
            return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = SystemHist()
        field_list = ["node_uuid", "kind", "kind_code", "backup_kind", "backup_kind_code", "zfs_mount_point", "image_name", "result", "result_code", "error", "error_code"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def update_systemhist(data, database_session):
        obj = database_session.query(SystemHist).filter(
            SystemHist.node_uuid == data.get('node_uuid')).first()
        field_list = ["node_uuid", "kind", "kind_code", "backup_kind", "backup_kind_code", "zfs_mount_point",
                      "image_name", "result", "result_code", "error", "error_code"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod
    def GetSystemHistory(data, database_session):
        query = database_session.query(SystemHist.node_uuid,
                                       SystemHist.kind,
                                       SystemHist.kind_code,
                                       SystemHist.backup_kind,
                                       SystemHist.backup_kind_code,
                                       SystemHist.zfs_ref_size,
                                       SystemHist.zfs_mount_point,
                                       SystemHist.image_name,
                                       SystemHist.result,
                                       SystemHist.result_code,
                                       SystemHist.error,
                                       SystemHist.error_code,
                                       SystemHist.register_dt)

        if 'node_uuid' in data:
            if data.get('node_uuid') is not None:
                query = query.filter(SystemHist.node_uuid == data.get('node_uuid'))

# repair required
        if 'target_type_list' in data:
            target_type_in = data.get('target_type_list')
            if isinstance(target_type_in, list):
                query = query.filter(SystemZfs.zfs_type.in_(target_type_in))

        query = query.all()
        field_list = ["node_uuid", "kind", "kind_code", "backup_kind", "backup_kind_code", "zfs_mount_point",
                      "image_name", "result", "result_code", "error", "error_code"]
        res = BaseDAO.return_data(query=query, field_list=field_list)

        return res

    @staticmethod  # @BaseDAO.database_operation
    def del_systemhist(data, database_session):
        try:
            data = database_session.query(SystemHist).filter(
                SystemHist.node_uuid == data.get('node_uuid')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'

class SystemZpoolPropertyDAO(BaseDAO):

    @staticmethod
    def register_zpool_property(data, database_session):

        obj = SystemPropertyZpool()
        field_list = [
            'meta_id', 'node_uuid', 'dataset', 'property', 'value', 'source'
        ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def get_bootfs(data, database_session):
        query = database_session.query(SystemPropertyZpool.value).\
            filter(SystemPropertyZpool.meta_id == data.get('meta_id')).\
            filter(SystemPropertyZpool.property == 'bootfs').first()
        return query

    @staticmethod
    def get_property(data, database_session):
        query = database_session.query(SystemPropertyZpool.node_uuid, SystemPropertyZpool.dataset,
                                       SystemPropertyZpool.property, SystemPropertyZpool.value,
                                       SystemPropertyZpool.source). \
            filter(SystemPropertyZpool.meta_id == data.get('meta_id')). \
            all()
        return query

    @staticmethod
    def delete_zpool_property(data, database_session):
        try:
            obj_list = database_session.query(SystemPropertyZpool).\
                filter(SystemPropertyZpool.meta_id == data.get('meta_id')).all()
            for obj in obj_list:
                BaseDAO.delete(obj, database_session)
        except Exception as e:
            return '0'
        return '1'


class SystemZfsPropertyDAO(BaseDAO):
    @staticmethod
    def register_zfs_property(data, database_session):

        obj = SystemPropertyZfs()
        field_list = [
            'meta_id', 'node_uuid', 'dataset', 'property', 'value', 'source'
        ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def get_property(data, database_session):
        query = database_session.query(SystemPropertyZfs.node_uuid, SystemPropertyZfs.dataset,
                                       SystemPropertyZfs.property, SystemPropertyZfs.value,
                                       SystemPropertyZfs.source). \
            filter(SystemPropertyZfs.meta_id == data.get('meta_id')). \
            all()
        return query

    @staticmethod
    def delete_zfs_property(data, database_session):
        try:
            obj_list = database_session.query(SystemPropertyZfs). \
                filter(SystemPropertyZfs.meta_id == data.get('meta_id')).all()
            for obj in obj_list:
                BaseDAO.delete(obj, database_session)
        except Exception as e:
            return '0'
        return '1'


class SystemMetaZpoolDAO(BaseDAO):
    @staticmethod
    def register_meta_zpool(data, database_session):
        obj = SystemBackupMetaZpool()
        field_list = [
            'meta_id', 'name', 'version', 'state', 'vdev_children'
        ]
        logger.info("=====================")
        BaseDAO.set_value(obj, field_list, data)
        logger.info("=====================")
        BaseDAO.insert(obj, database_session)
        logger.info("=====================")
        return obj.vdev_tree_uuid

    @staticmethod
    def get_zpool_name(data, database_session):
        query = database_session.query(SystemBackupMetaZpool.name). \
            filter(SystemBackupMetaZpool.meta_id == data.get('meta_id')). \
            all()
        return query

    @staticmethod
    def delete_meta_zpool(data, database_session):
        try:
            obj_list = database_session.query(SystemBackupMetaZpool). \
                filter(SystemBackupMetaZpool.meta_id == data.get('meta_id')).all()
            for obj in obj_list:
                BaseDAO.delete(obj, database_session)
        except Exception as e:
            return '0'
        return '1'


class SystemMetaVdevTreeDAO(BaseDAO):

    @staticmethod
    def register_meta_vdevtree(data, database_session):
        obj = SystemBackupMetaVdevTree()
        field_list = [
            'meta_id', 'guid', 'type', 'vdev_tree_uuid'
        ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.vdev_tree_uuid

    @staticmethod
    def get_type_and_tree_uuid(data, database_session):
        query = database_session.query(SystemBackupMetaVdevTree.type, SystemBackupMetaVdevTree.vdev_tree_uuid). \
            filter(SystemBackupMetaVdevTree.meta_id == data.get('meta_id')). \
            all()
        return query

    @staticmethod
    def delete_meta_vdevtree(data, database_session):
        try:
            obj_list = database_session.query(SystemBackupMetaVdevTree). \
                filter(SystemBackupMetaVdevTree.meta_id == data.get('meta_id')).all()
            for obj in obj_list:
                BaseDAO.delete(obj, database_session)
        except Exception as e:
            return '0'
        return '1'

class SystemMetaChildrenDAO(BaseDAO):

    @staticmethod
    def register_meta_children(data, database_session):
        obj = SystemBackupMetaChildren()
        field_list = [
            'meta_id', 'children_id', 'guid', 'type', 'ashift', 'asize', 'nparity',
            'vdev_tree_uuid', 'is_children_sub', 'path'
        ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.children_sub_uuid

    @staticmethod
    def get_is_children_sub_list(data, database_session):
        query = database_session.query(SystemBackupMetaChildren.is_children_sub). \
            filter(SystemBackupMetaChildren.meta_id == data.get('meta_id')). \
            filter(SystemBackupMetaChildren.vdev_tree_uuid == data.get('vdev_tree_uuid')). \
            all()
        return query

    @staticmethod
    def get_ashift(data, database_session):
        query = database_session.query(SystemBackupMetaChildren.ashift,
                                       SystemBackupMetaChildren.children_id,
                                       SystemBackupMetaChildren.is_children_sub). \
            filter(SystemBackupMetaChildren.meta_id == data.get('meta_id')). \
            filter(SystemBackupMetaChildren.vdev_tree_uuid == data.get('vdev_tree_uuid')). \
            all()
        return query


    @staticmethod
    def delete_meta_children(data, database_session):
        try:
            obj_list = database_session.query(SystemBackupMetaChildren). \
                filter(SystemBackupMetaChildren.meta_id == data.get('meta_id')).all()
            for obj in obj_list:
                BaseDAO.delete(obj, database_session)
        except Exception as e:
            return '0'
        return '1'



class SystemBackupChildrenSubDAO(BaseDAO):

    @staticmethod
    def register_meta_children_sub(data, database_session):
        obj = SystemBackupMetaChildrenSub()
        field_list = [
            'meta_id', 'children_sub_id', 'guid', 'type', 'path', 'vdev_tree_uuid', 'children_sub_uuid'
        ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def get_device_path_list(data, database_session):
        query = database_session.query(SystemBackupMetaChildrenSub.children_sub_id,
                                       SystemBackupMetaChildrenSub.path). \
            filter(SystemBackupMetaChildrenSub.meta_id == data.get('meta_id')). \
            filter(SystemBackupMetaChildrenSub.vdev_tree_uuid == data.get('vdev_tree_uuid')). \
            filter(SystemBackupMetaChildrenSub.children_sub_uuid == data.get('children_sub_uuid')). \
            all()
        return query

    @staticmethod
    def delete_meta_children_sub(data, database_session):
        try:
            obj_list = database_session.query(SystemBackupMetaChildrenSub). \
                filter(SystemBackupMetaChildrenSub.meta_id == data.get('meta_id')).all()
            for obj in obj_list:
                BaseDAO.delete(obj, database_session)
        except Exception as e:
            return '0'
        return '1'

class SystemZpoolListHvDAO(BaseDAO):

    @staticmethod
    def register_zpool_list_hv(data, database_session):
        obj = SystemZpoolListHv()
        field_list = [
            'meta_id', 'pool', 'method', 'create_cnt', 'device'
        ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def delete_zpool_list_hv(data, database_session):
        try:
            obj_list = database_session.query(SystemZpoolListHv). \
                    filter(SystemZpoolListHv.meta_id == data.get('meta_id')).all()
            for obj in obj_list:
                BaseDAO.delete(obj, database_session)
        except Exception as e:
            return '0'
        return '1'

class SystemGeomListDAO(BaseDAO):

    @staticmethod
    def register_geom_list(data, database_session):
        obj = SystemGeomList()
        field_list = [
            'meta_id', 'geom_name', 'providers', 'name',
            'mediasize', 'sectorsize', 'mode', 'descr',
            'ident', 'rotationrate', 'fwsectors', 'fwheads'
        ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def delete_geom_list(data, database_session):
        try:
            obj_list = database_session.query(SystemGeomList). \
                filter(SystemGeomList.meta_id == data.get('meta_id')).all()
            for obj in obj_list:
                BaseDAO.delete(obj, database_session)
        except Exception as e:
            return '0'
        return '1'


class SystemGpartBackupDAO(BaseDAO):
    @staticmethod
    def register_gpart_backup(data, database_session):
        obj = SystemGpartBackup()
        field_list = [
            'meta_id', 'device', 'gpart_file_name', 'gpart_file_size', 'gpart_path'
        ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def delete_gpart_backup(data, database_session):
        try:
            obj_list = database_session.query(SystemGpartBackup). \
                filter(SystemGpartBackup.meta_id == data.get('meta_id')).all()
            for obj in obj_list:
                BaseDAO.delete(obj, database_session)
        except Exception as e:
            return '0'
        return '1'


########################################### HISTORY AND PROCESS CHECK ##############################

class SystemProcessStatusDAO(BaseDAO):
    @staticmethod
    def start_process(data, database_session):
        obj = SystemProcessStatus()
        field_list = [
            'server_uuid', 'target_uuid', 'nodetype', 'usetype', 'name', 'kind',
            'action_kind', 'action_message', 'action_status'
        ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def get_status(data, database_session):
        query = database_session.query(SystemProcessStatus.action_status).\
            filter(SystemProcessStatus.id == data.get('run_uuid')).\
            first()
        return query

    @staticmethod
    def gethistory(data, database_session):
        query = database_session.query(SystemProcessStatus.name,
                                       SystemProcessStatus.nodetype,
                                       SystemProcessStatus.usetype,
                                       SystemProcessStatus.target_uuid,
                                       SystemProcessStatus.action_kind,
                                       SystemProcessStatus.action_message,
                                       SystemProcessStatus.action_status,
                                       SystemProcessStatus.register_dt,
                                       SystemProcessStatus.update_dt
                                       )
        query = query.filter(SystemProcessStatus.kind == data.get('kind'))
        target_status = ['END', 'ERROR']
        query = query.filter(SystemProcessStatus.action_status.in_(target_status))
        if 'namelist' in data:
            namelist = data.get('namelist')
            query = query.filter(SystemProcessStatus.name.in_(namelist))

        query = query.order_by(SystemProcessStatus.register_dt.desc()).all()
        field_list = [
            'name', 'nodetype', 'usetype', 'uuid', 'kind', 'message',
            'status', 'startat', 'endat'
        ]
        result = BaseDAO.return_data(query=query, field_list=field_list)

        return result

    @staticmethod
    def update_process(data, database_session):
        run_uuid = data.get('run_uuid')
        obj = database_session.query(SystemProcessStatus).\
            filter(SystemProcessStatus.id == run_uuid).\
            first()
        field_list = [
            'action_message', 'action_status'
        ]
        BaseDAO.update_value(obj, field_list, data)
        obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.id

    @staticmethod
    def end_process(data, database_session):
        try:
            obj = database_session.query(SystemProcessStatus).\
            filter(SystemProcessStatus.id == data.get('run_uuid')).\
            first()
            BaseDAO.delete(obj, database_session)
        except Exception as e:
            return '0'
        return '1'


class SystemProcessStatusHistDAO(BaseDAO):
    @staticmethod
    def register_process_hist(data, database_session):
        obj = SystemProcessStatusHist()
        field_list = [
            'run_uuid',
            'server_uuid', 'target_uuid', 'nodetype', 'usetype', 'name', 'kind',
            'action_kind', 'action_message', 'action_status'
        ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def get_process_hist(data, database_session):
        empty_value = '-'
        query = database_session.query( SystemProcessStatusHist.name,
                                        SystemProcessStatusHist.nodetype,
                                        SystemProcessStatusHist.usetype,
                                        SystemProcessStatusHist.action_kind,
                                        SystemProcessStatusHist.action_status,
                                        SystemProcessStatusHist.action_message,
                                        SystemProcessStatusHist.register_dt
                                       )
        if 'run_uuid' in data:
            if data.get('run_uuid') is not None:
                query = query.filter(func.lower(SystemProcessStatusHist.run_uuid) == data.get('run_uuid').lower())

        if 'kind' in data:
            if data.get('kind') is not None:
                query = query.filter(SystemProcessStatusHist.kind == data.get('kind'))

        if 'namelist' in data:
            namelist = data.get('namelist')
            query = query.filter(SystemProcessStatusHist.name.in_(namelist))

        if 'limit' in data:
            limit_cnt = int(data.get('limit'))
            if limit_cnt > 0:
                query = query.limit(limit_cnt)

        query = query.order_by(SystemProcessStatusHist.register_dt.desc()).all()
        field_list = [
            'name', 'nodetype', 'usetype', 'action_kind', 'action_status', 'action_message', 'register_dt'
        ]
        result = BaseDAO.return_data(query=query, field_list=field_list)

        for res_raw in result:
            res_raw['err_code'] = '-'
            res_raw['err_message'] = '-'

        return result

    @staticmethod
    def getrealhist(data, database_session):
        empty_value = '-'
        query = database_session.query(SystemProcessStatusHist.name,
                                       SystemProcessStatusHist.nodetype,
                                       SystemProcessStatusHist.usetype,
                                       SystemProcessStatusHist.action_kind,
                                       SystemProcessStatusHist.action_status,
                                       SystemProcessStatusHist.action_message,
                                       SystemProcessStatusHist.register_dt
                                       )
        if 'run_uuid' in data:
            if data.get('run_uuid') is not None:
                query = query.filter(SystemProcessStatusHist.run_uuid == data.get('run_uuid'))

        logger.info("RUN_UUID : {}".format(data.get('run_uuid')))
        query = query.order_by(SystemProcessStatusHist.register_dt.desc()).all()
        field_list = [
            'name', 'nodetype', 'usetype', 'kind', 'status', 'message', 'start'
        ]
        result = BaseDAO.return_data(query=query, field_list=field_list)

        for res_raw in result:
            res_raw['err_code'] = '-'
            res_raw['err_message'] = '-'

        return result

    @staticmethod
    def delete_process_hist(data, database_session):
        try:
            obj = database_session.query(SystemProcessStatusHist). \
                filter(SystemProcessStatusHist.id == data.get('hist_id')). \
                first()
            BaseDAO.delete(obj, database_session)
        except Exception as e:
            return '0'
        return '1'


class SystemProcessStatusErrHistDAO(BaseDAO):
    @staticmethod
    def register_process_hist_err(data, database_session):
        obj = SystemProcessStatusErrHist()
        field_list = [
            'run_uuid',
            'server_uuid', 'target_uuid', 'nodetype', 'usetype', 'name', 'kind',
            'action_kind', 'action_message', 'action_status', 'err_code',
            'err_message'
        ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def get_process_hist_err(data, database_session):
        query = database_session.query(SystemProcessStatusErrHist.name,
                                       SystemProcessStatusErrHist.nodetype,
                                       SystemProcessStatusErrHist.usetype,
                                       SystemProcessStatusErrHist.action_kind,
                                       SystemProcessStatusErrHist.action_status,
                                       SystemProcessStatusErrHist.action_message,
                                       SystemProcessStatusErrHist.err_code,
                                       SystemProcessStatusErrHist.err_message,
                                       SystemProcessStatusErrHist.register_dt
                                       )

        if 'run_uuid' in data:
            if data.get('run_uuid') is not None:
                query = query.filter(SystemProcessStatusErrHist.run_uuid == data.get('run_uuid'))

        if 'kind' in data:
            if data.get('kind') is not None:
                query = query.filter(SystemProcessStatusErrHist.kind == data.get('kind'))

        if 'namelist' in data:
            namelist = data.get('namelist')
            query = query.filter(SystemProcessStatusErrHist.name.in_(namelist))

        if 'limit' in data:
            limit_cnt = int(data.get('limit'))
            if limit_cnt > 0:
                query = query.limit(limit_cnt)

        query = query.order_by(SystemProcessStatusErrHist.register_dt.desc()).all()

        field_list = [
            'name', 'nodetype', 'usetype', 'action_kind', 'action_status', 'action_message',
            'err_code', 'err_message', 'register_dt'
        ]

        res = BaseDAO.return_data(query=query, field_list=field_list)

        return res

    @staticmethod
    def getrealhist(data, database_session):
        query = database_session.query(SystemProcessStatusErrHist.name,
                                       SystemProcessStatusErrHist.nodetype,
                                       SystemProcessStatusErrHist.usetype,
                                       SystemProcessStatusErrHist.action_kind,
                                       SystemProcessStatusErrHist.action_status,
                                       SystemProcessStatusErrHist.action_message,
                                       SystemProcessStatusErrHist.err_code,
                                       SystemProcessStatusErrHist.err_message,
                                       SystemProcessStatusErrHist.register_dt
                                       )

        if 'run_uuid' in data:
            if data.get('run_uuid') is not None:
                query = query.filter(SystemProcessStatusErrHist.run_uuid == data.get('run_uuid'))

        query = query.order_by(SystemProcessStatusErrHist.register_dt.desc()).all()

        field_list = [
            'name', 'nodetype', 'usetype', 'kind', 'status', 'message',
            'err_code', 'err_message', 'start'
        ]

        res = BaseDAO.return_data(query=query, field_list=field_list)

        return res

    @staticmethod
    def delete_process_hist_err(data, database_session):
        try:
            obj = database_session.query(SystemProcessStatusErrHist). \
                filter(SystemProcessStatusErrHist.id == data.get('hist_id')). \
                first()
            BaseDAO.delete(obj, database_session)
        except Exception as e:
            return '0'
        return '1'