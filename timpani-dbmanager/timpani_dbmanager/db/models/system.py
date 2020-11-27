from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, CHAR
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func

from . import Base

class System(Base):
    __tablename__ = "tb_system"

    id = Column(Integer, primary_key=True)
    node_uuid = Column(String(64))
    #node = relationship("Node", back_populates="system")
    meta_id = Column(Integer)
    # backupmeta = relationship("SystemBackupMeta", back_populates="system")
    # Agent Collection Information
    ipv4address = Column(String(64))
    os_type = Column(String(32))
    os_type_code = Column(String(32))
    os_name = Column(String(32))
    os_version = Column(String(32))
    os_arch = Column(String(32))
    os_arch_code = Column(String(32))
    kernel_version = Column(String(32))
    hostname = Column(String(32))
    register_dt = Column(DateTime(timezone=True), default=func.now())

def generate_uuid():
    return str(uuid.uuid4()).replace('-', '')

class Agent(Base):
    __tablename__ = "tb_agent"

    uuid = Column(String(64), primary_key=True, default=generate_uuid, nullable=False)
    capability = Column(String(64))
    capability_code = Column(String(32))
    ipv4address = Column(String(32))
    ipv4port = Column(String(8), nullable=True)
    node_uuid = Column(String(64), nullable=False)
    start_dt = Column(DateTime(timezone=True), default=func.now())
    end_dt = Column(DateTime(timezone=True), nullable=True)

class SystemZfs(Base):                  # zfs list -t filesystem
    __tablename__ = "tb_system_zfs"

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer)
    zfs_used_size = Column(String(64))
    zfs_avail_size = Column(String(64))
    zfs_mount_point = Column(String(256))
    zfs_name = Column(String(256))
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemPropertyZfs(Base):
    __tablename__ = "tb_system_property_zfs"

    id = Column(Integer, primary_key=True)

    # Name Property value source
    node_uuid = Column(String(64), nullable=False)
    dataset = Column(String(64), nullable=False)
    property = Column(String(32), nullable=False)
    value = Column(String(32), nullable=True)
    source = Column(String(32), nullable=True)

class SystemPropertyZpool(Base):
    __tablename__ = "tb_system_property_zpool"

    id = Column(Integer, primary_key=True)

    # Name Property value source
    node_uuid = Column(String(64), nullable=False)
    dataset = Column(String(64), nullable=False)
    property = Column(String(32), nullable=False)
    value = Column(String(32), nullable=True)
    source = Column(String(32), nullable=True)


class SystemDisk(Base):
    __tablename__ = "tb_system_disk"

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer)
    disk_used = Column(String(64))
    disk_free = Column(String(64))
    disk_avail = Column(String(64))
    register_dt = Column(DateTime(timezone=True), default=func.now())


class SystemBackupMeta(Base):
    __tablename__ = "tb_system_backup_meta"

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer)
    backup_kind = Column(String(32), nullable=False)
    backup_kind_code = Column(String(32))
    zfs_mount_point = Column(String(256))
    image_name = Column(String(128))
    zfs_name = Column(String(256))
    zfs_used_size = Column(String(64))
    zfs_avail_size = Column(String(64))
    register_dt = Column(DateTime(timezone=True), default=func.now())
    image_id = Column(Integer)
    #image = relationship("SystemBackupImage", back_populates="meta")
    #system = relationship("System", back_populates="backupmeta")

class SystemBackupImage(Base):
    __tablename__ = "tb_system_backup_image"

    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer)
    #meta = relationship("SystemBackupMeta", uselist=False, back_populates="image")
    image_kind = Column(String(32), nullable=False)
    image_kind_code = Column(String(32))
    image_hash = Column(String(256), nullable=False)
    image_name = Column(String(128), nullable=False)
    image_size = Column(String(64), nullable=True)
    image_path = Column(String(256), nullable=False)
    register_dt = Column(DateTime(timezone=True), default=func.now())
    parent_id = Column(Integer)
    #parent = relationship("SystemBackupImage", backref=backref("child"))

class SystemHist(Base):
    __tablename__ = "tb_system_hist"

    id = Column(Integer, primary_key=True)
    node_uuid = Column(String(64))
    kind = Column(String(32), nullable=False)
    kind_code = Column(String(32))
    backup_kind = Column(String(32), nullable=False)
    backup_kind_code = Column(String(32))
    zfs_mount_point = Column(String(256))
    image_name = Column(String(128))
    result = Column(String(32))
    result_code = Column(String(32))
    register_dt = Column(DateTime(timezone=True), default=func.now())
    error = Column(String(256))
    error_code = Column(String(32))

__all__ = [ 'System', 'Agent', 'SystemZfs', 'SystemDisk', 'SystemBackupMeta', 'SystemBackupImage',
            'SystemPropertyZfs', 'SystemPropertyZpool','SystemHist']