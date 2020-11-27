import logging
from .base_dao import BaseDAO
from ..models.system import (System, SystemBackupImage, SystemBackupMeta, SystemDisk, SystemHist, SystemZfs, Agent)
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

# class System(Base):
#     __tablename__ = "tb_system"
#
#     id = Column(Integer, primary_key=True)
#     node_uuid = Column(CHAR(32), ForeignKey('tb_node.uuid'))
#     #node = relationship("Node", back_populates="system")
#     meta_id = Column(Integer, ForeignKey('tb_system_backup_meta.id'))
#     # backupmeta = relationship("SystemBackupMeta", back_populates="system")
#     # Agent Collection Information
#     ipv4address = Column(String(64))
#     os_type = Column(String(32))
#     os_type_code = Column(String(32))
#     os_version = Column(String(32))
#     os_arch = Column(String(32))
#     os_arch_code = Column(String(32))
#     kernel_version = Column(String(32))
#     register_dt = Column(DateTime(timezone=True), default=func.now())

class agentDAO(BaseDAO):

    @staticmethod
    def registerAgent(data, database_session):
        obj = Agent()
        field_list = ["uuid", "capability", "capability_code", "ipv4address", "ipv4port", "node_uuid"]
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

    @staticmethod  # @BaseDAO.database_operation
    def del_system(data, database_session):
        try:
            data = database_session.query(System).filter(
                System.node_uuid == data.get('node_uuid')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'
#
# def generate_uuid():
#     return str(uuid.uuid4())
#
# class Agent(Base):
#     __tablename__ = "tb_agent"
#
#     uuid = Column(CHAR(32), primary_key=True, default=generate_uuid, nullable=False)
#     capability = Column(String(64))
#     capability_code = Column(String(32))
#     ipv4address = Column(String(32))
#     ipv4port = Column(String(8))
#     start_dt = Column(DateTime(timezone=True), default=func.now())
#     end_dt = Column(DateTime(timezone=True), nullable=True)

class AgentDAO(BaseDAO):
    @staticmethod
    def register_agent(data, database_session):
        list = database_session.query(Agent).filter(
            Agent.uuid == data.get('uuid')).all()
        logger.info("list size : {} === {}".format(len(list), list))
        if len(list) != 0:
            return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = Agent()
        field_list = ["uuid", "capability", "capability_code", "ipv4address", "ipv4port"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def update_agent(data, database_session):
        obj = database_session.query(Agent).filter(
            Agent.uuid == data.get('uuid')).first()
        field_list = ["uuid", "capability", "capability_code", "ipv4address", "ipv4port", "end_dt"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def del_agent(data, database_session):
        try:
            data = database_session.query(Agent).filter(
                Agent.uuid == data.get('uuid')).first()
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
    def register_system(data, database_session):
        list = database_session.query(SystemZfs).filter(
            SystemZfs.system_id == data.get('system_id')).all()
        logger.info("list size : {} === {}".format(len(list), list))
        if len(list) != 0:
            return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = SystemZfs()
        field_list = ["node_uuid", "meta_id", "ipv4address", "os_type", "os_type_code", "os_arch",
                      "os_arch_code", "kernel_version"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def update_system(data, database_session):
        obj = database_session.query(SystemZfs).filter(
            SystemZfs.node_uuid == data.get('node_uuid')).first()
        field_list = ["node_uuid", "meta_id", "ipv4address", "os_type", "os_type_code", "os_arch",
                      "os_arch_code",
                      "kernel_version"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def del_system(data, database_session):
        try:
            data = database_session.query(SystemZfs).filter(
                SystemZfs.node_uuid == data.get('node_uuid')).first()
            BaseDAO.delete(data, database_session)
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
        list = database_session.query(SystemBackupMeta).filter(
            SystemBackupMeta.system_id == data.get('system_id')).all()
        logger.info("list size : {} === {}".format(len(list), list))
        if len(list) != 0:
            return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = SystemBackupMeta()
        field_list = ["system_id","backup_kind", "backup_kind_code", "zfs_mount_point", "image_name", "zfs_name", "zfs_used_size", "zfs_avail_size", "image_id"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.system_id

    @staticmethod  # @BaseDAO.database_operation
    def update_systembackupmeta(data, database_session):
        obj = database_session.query(SystemBackupMeta).filter(
            SystemBackupMeta.system_id == data.get('system_id')).first()
        field_list = ["system_id", "backup_kind", "backup_kind_code", "zfs_mount_point", "image_name", "zfs_name",
                      "zfs_used_size", "zfs_avail_size", "image_id"]
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

# class SystemBackupImage(Base):
#     __tablename__ = "tb_system_backup_image"
#
#     id = Column(Integer, primary_key=True)
#     meta_id = Column(Integer, ForeignKey('tb_system_backup_meta.id'))
#     #meta = relationship("SystemBackupMeta", uselist=False, back_populates="image")
#     image_kind = Column(String(32), nullable=False)
#     image_kind_code = Column(String(32))
#     image_hash = Column(String(256), nullable=False)
#     image_name = Column(String(128), nullable=False)
#     image_size = Column(String(64), nullable=True)
#     image_path = Column(String(256), nullable=False)
#     register_dt = Column(DateTime(timezone=True), default=func.now())
#     parent_id = Column(Integer, ForeignKey('tb_system_backup_image.id'))
#     #parent = relationship("SystemBackupImage", backref=backref("child"))

class SystemBakupImageDAO(BaseDAO):
    @staticmethod
    def register_systembackupimage(data, database_session):
        list = database_session.query(SystemBackupImage).filter(
            SystemBackupImage.meta_id == data.get('meta_id')).all()
        logger.info("list size : {} === {}".format(len(list), list))
        if len(list) != 0:
            return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = SystemBackupImage()
        field_list = ["meta_id", "image_kind", "image_kind_code", "image_hash", "image_name", "image_size", "image_path", "parent_id"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.meta_id

    @staticmethod  # @BaseDAO.database_operation
    def update_systembackupimage(data, database_session):
        obj = database_session.query(SystemBackupImage).filter(
            SystemBackupImage.meta_id == data.get('meta_id')).first()
        field_list = ["meta_id", "image_kind", "image_kind_code", "image_hash", "image_name", "image_size",
                      "image_path", "parent_id"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.meta_id

    @staticmethod  # @BaseDAO.database_operation
    def del_systembackupimage(data, database_session):
        try:
            data = database_session.query(SystemBackupImage).filter(
                SystemBackupImage.meta_id == data.get('meta_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'
            
# class SystemHist(Base):
#     __tablename__ = "tb_system_hist"
#
#     id = Column(Integer, primary_key=True)
#     node_uuid = Column(CHAR(32), ForeignKey('tb_node.uuid'))
#     kind = Column(String(32), nullable=False)
#     kind_code = Column(String(32))
#     backup_kind = Column(String(32), nullable=False)
#     backup_kind_code = Column(String(32))
#     zfs_mount_point = Column(String(256))
#     image_name = Column(String(128))
#     result = Column(String(32))
#     result_code = Column(String(32))
#     register_dt = Column(DateTime(timezone=True), default=func.now())
#     error = Column(String(256))
#     error_code = Column(String(32))


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

    @staticmethod  # @BaseDAO.database_operation
    def del_systemhist(data, database_session):
        try:
            data = database_session.query(SystemHist).filter(
                SystemHist.node_uuid == data.get('node_uuid')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'
