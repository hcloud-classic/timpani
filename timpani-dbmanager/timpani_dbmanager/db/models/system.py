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
    macaddress = Column(String(32), nullable=True)
    pid = Column(String(16), nullable=True)
    node_uuid = Column(String(64), nullable=False)
    start_dt = Column(DateTime(timezone=True), default=func.now())
    end_dt = Column(DateTime(timezone=True), nullable=True)

class SystemZfs(Base):                  # zfs list -t filesystem
    __tablename__ = "tb_system_zfs"

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer)
    node_uuid = Column(String(64), nullable=False)
    zfs_used_size = Column(String(64), nullable=True)
    zfs_avail_size = Column(String(64), nullable=True)
    zfs_ref_size = Column(String(64), nullable=True)
    zfs_type = Column(String(64), nullable=True)
    zfs_type_code = Column(Integer, nullable=True)         # 0:FileSystem, 1: Volume, 2: Snapshot
    zfs_mount_point = Column(String(256), nullable=True)
    zfs_name = Column(String(128), nullable=True)
    zpool_name = Column(String(64), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemPropertyZfs(Base):
    __tablename__ = "tb_system_property_zfs"

    id = Column(Integer, primary_key=True)

    # Name Property value source
    meta_id = Column(Integer, nullable=False)
    node_uuid = Column(String(64), nullable=False)
    dataset = Column(String(64), nullable=False)
    property = Column(String(32), nullable=False)
    value = Column(String(32), nullable=True)
    source = Column(String(32), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemPropertyZpool(Base):
    __tablename__ = "tb_system_property_zpool"

    id = Column(Integer, primary_key=True)

    # Name Property value source
    meta_id = Column(Integer, nullable=False)
    node_uuid = Column(String(64), nullable=False)
    dataset = Column(String(64), nullable=False)
    property = Column(String(32), nullable=False)
    value = Column(String(32), nullable=True)
    source = Column(String(32), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())


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
    system_id = Column(Integer, nullable=True)
    node_uuid = Column(String(64), nullable=True)
    backup_kind = Column(String(32), nullable=False)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemBackupMetaZpool(Base):

    __tablename__ = "tb_system_backup_meta_zpool"

    id = Column(Integer, primary_key=True, nullable=False)
    meta_id = Column(Integer, nullable=False)
    name = Column(String(32), nullable=False)
    version = Column(String(32), nullable=True)
    state = Column(String(32), nullable=True)
    vdev_children = Column(String(32), nullable=True)
    vdev_tree_uuid = Column(String(64), default=generate_uuid, nullable=False)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemBackupMetaVdevTree(Base):
    __tablename__ = "tb_system_backup_meta_vdevtree"

    id = Column(Integer, primary_key=True, nullable=False)
    meta_id = Column(Integer, nullable=False)
    guid = Column(String(32), nullable=False)
    type = Column(String(32), nullable=False)
    vdev_tree_uuid = Column(String(64), nullable=False)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemBackupMetaChildren(Base):
    __tablename__ = "tb_system_backup_meta_children"

    id = Column(Integer, primary_key=True, nullable=False)
    meta_id = Column(Integer, nullable=False)
    children_id = Column(String(32), nullable=True)
    guid = Column(String(32), nullable=True)
    type = Column(String(32), nullable=True)
    ashift = Column(String(32), nullable=True)
    asize = Column(String(32), nullable=True)
    nparity = Column(String(32), nullable=True)
    path = Column(String(32), nullable=True)
    vdev_tree_uuid = Column(String(64), nullable=False)
    children_sub_uuid = Column(String(64), default=generate_uuid, nullable=False)
    is_children_sub = Column(String(32), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())


class SystemBackupMetaChildrenSub(Base):
    __tablename__ = "tb_system_backup_meta_children_sub"

    id = Column(Integer, primary_key=True, nullable=False)
    meta_id = Column(Integer, nullable=False)
    children_sub_id = Column(String(32), nullable=False)
    guid = Column(String(32), nullable=False)
    type = Column(String(32), nullable=False)
    path = Column(String(256), nullable=False)
    vdev_tree_uuid = Column(String(64), nullable=False)
    children_sub_uuid = Column(String(64), nullable=False)
    register_dt = Column(DateTime(timezone=True), default=func.now())


class SystemBackupImage(Base):
    __tablename__ = "tb_system_backup_image"

    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer, nullable=False)
    zpool_name = Column(String(32), nullable=True)
    dataset = Column(String(64), nullable=True)
    image_kind = Column(String(32), nullable=False)
    image_kind_code = Column(String(32), nullable=True)
    image_hash = Column(String(256), nullable=True)
    image_name = Column(String(128), nullable=False)
    image_size = Column(String(64), nullable=True)
    image_path = Column(String(256), nullable=False)
    parent_image_name = Column(String(128), default='-', nullable=True)
    parent_id = Column(Integer, default=0, nullable=True)
    child_id = Column(Integer, default=0, nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemBackupSnapshotList(Base):
    __tablename__ = "tb_system_backup_snapshot_list"

    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer, nullable=False)
    index = Column(Integer, nullable=False)
    start_dataset = Column(String(64), nullable=True)
    dataset = Column(String(64), nullable=True)
    snapname = Column(String(64), nullable=True)
    snapshot_name = Column(String(64), nullable=True)
    create_time = Column(String(64), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())



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

class SystemProcessStatus(Base):

    __tablename__ = "tb_system_process_status"
    __table_args__ = {'extend_existing': True}

    id = Column(String(64), primary_key=True, default=generate_uuid, nullable=False)
    server_uuid = Column(String(64), nullable=True)
    target_uuid = Column(String(64), nullable=True)
    nodetype = Column(String(32), nullable=True)
    usetype = Column(String(32), nullable=True)
    name = Column(String(512), nullable=True)
    kind = Column(String(32), nullable=True)
    action_kind = Column(String(32), nullable=False)
    action_message = Column(String(256), nullable=False)
    action_status = Column(String(32), nullable=False)
    register_dt = Column(DateTime(timezone=True), default=func.now())
    update_dt = Column(DateTime(timezone=True), default=func.now(), nullable=True)


class SystemProcessStatusHist(Base):

    __tablename__ = "tb_system_process_status_hist"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, nullable=False)
    run_uuid = Column(String(64), nullable=True)
    server_uuid = Column(String(64), nullable=True)
    target_uuid = Column(String(64), nullable=True)
    nodetype = Column(String(32), nullable=True)
    usetype = Column(String(32), nullable=True)
    name = Column(String(512), nullable=True)
    kind = Column(String(32), nullable=True)
    action_kind = Column(String(32), nullable=False)
    action_message = Column(String(256), nullable=False)
    action_status = Column(String(32), nullable=False)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemProcessStatusErrHist(Base):

    __tablename__ = "tb_system_process_status_err_hist"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, nullable=False)
    run_uuid = Column(String(64), nullable=True)
    server_uuid = Column(String(64), nullable=True)
    target_uuid = Column(String(64), nullable=True)
    nodetype = Column(String(32), nullable=True)
    usetype = Column(String(32), nullable=True)
    name = Column(String(512), nullable=True)
    kind = Column(String(32), nullable=True)
    action_kind = Column(String(32), nullable=False)
    action_message = Column(String(256), nullable=False)
    action_status = Column(String(32), nullable=False)
    err_code = Column(String(32), nullable=False)
    err_message = Column(String(256), nullable=False)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemZpoolListHv(Base):

    __tablename__ = "tb_system_zpool_list_hv"

    id = Column(Integer, primary_key=True, nullable=False)
    meta_id = Column(Integer, nullable=False)
    pool = Column(String(32), nullable=False)
    method = Column(String(32), nullable=False)
    create_cnt = Column(String(32), nullable=True)
    device = Column(String(256), nullable=False)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemGeomList(Base):

    __tablename__ = "tb_system_geom_list"

    id = Column(Integer, primary_key=True, nullable=False)
    meta_id = Column(Integer, nullable=False)
    geom_name = Column(String(32), nullable=False)
    providers = Column(String(32), nullable=True)
    name = Column(String(32), nullable=False)
    mediasize = Column(String(32), nullable=True)
    sectorsize = Column(String(32), nullable=True)
    mode = Column(String(32), nullable=True)
    descr = Column(String(128), nullable=True)
    ident = Column(String(32), nullable=True)
    rotationrate = Column(String(32), nullable=True)
    fwsectors = Column(String(32), nullable=True)
    fwheads = Column(String(32), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemGpartBackup(Base):

    __tablename__ = "tb_system_gpart_backup"

    id = Column(Integer, primary_key=True, nullable=False)
    meta_id = Column(Integer, nullable=False)
    device = Column(String(32), nullable=False)
    gpart_file_name = Column(String(128), nullable=False)
    gpart_file_size = Column(String(32), nullable=False)
    gpart_path = Column(String(256), nullable=False)
    register_dt = Column(DateTime(timezone=True), default=func.now())

# ADD LINUX DATA
class SystemLinuxRsyncBackup(Base):

    __tablename__ = "tb_system_rsync_linux_backup"

    id = Column(Integer, primary_key=True, nullable=False)
    meta_id = Column(Integer, nullable=False)
    target = Column(String(32), nullable=True)
    snap_name = Column(String(32), nullable=True)
    snap_target =Column(String(64), nullable=True)
    ref_path = Column(String(256), nullable=True)
    parent_ref_path = Column(String(256), nullable=True)
    home_path = Column(String(128), nullable=True)
    backup_date = Column(String(32), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SystemLinuxPartBackup(Base):

    __tablename__ = "tb_system_part_linux_backup"

    id = Column(Integer, primary_key=True, nullable=False)
    meta_id = Column(Integer, nullable=False)
    mountpoint = Column(String(128), nullable=True)
    subsystems = Column(String(64), nullable=True)
    type = Column(String(32), nullable=True)
    file_part_path = Column(String(256), nullable=True)
    name = Column(String(32), nullable=True)
    tran = Column(String(32), nullable=True)
    uuid = Column(String(128), nullable=True)
    fstype = Column(String(32), nullable=True)
    label = Column(String(32), nullable=True)
    kname = Column(String(32), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())


__all__ = [ 'System', 'Agent', 'SystemZfs', 'SystemDisk', 'SystemBackupMeta', 'SystemBackupImage',
            'SystemPropertyZfs', 'SystemPropertyZpool','SystemHist',
            'SystemBackupMetaZpool', 'SystemBackupMetaVdevTree', 'SystemBackupMetaChildren',
            'SystemBackupMetaChildrenSub', 'SystemProcessStatus', 'SystemProcessStatusHist',
            'SystemProcessStatusErrHist', 'SystemLinuxRsyncBackup', 'SystemLinuxPartBackup'
            ]