from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, BIGINT
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql.types import MEDIUMBLOB

from . import Base

class MetaPool(Base):       # pool
    __tablename__ = "tb_meta_pool"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    sub_id = Column(Integer)
    pool = Column(String(64))
    ashift = Column(Integer)
    create_option = Column(String(512))
    tree_id = Column(Integer, default=0)

class MetaDeviceTree(Base):
    __tablename__ = "tb_meta_device_tree"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    uuid = Column(String(64), nullable=False)  # Node UUID
    tree_id = Column(Integer)
    treetype = Column(String(64))
    treetype_id = Column(Integer)
    disk_id = Column(Integer)
    device_path = Column(String(128))

class MetaTargetProperty(Base):
    __tablename__ = "tb_meta_target_property"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    pool = Column(String(64))
    name = Column(String(256), nullable=True)       # volume name
    dataset = Column(String(256), nullable=True)    # dataset name
    zfstype = Column(String(32), nullable=True)
    sub_id = Column(Integer)
    property = Column(String(32), nullable=False)
    value = Column(String(32), nullable=True)
    source = Column(String(32), nullable=True)


class MetaPoolProperty(Base):

    __tablename__ = "tb_meta_pool_property"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    pool = Column(String(64), nullable=False)
    sub_id = Column(Integer)
    property = Column(String(32), nullable=False)
    value = Column(String(32), nullable=True)
    source = Column(String(32), nullable=True)

class MetaData(Base):

    __tablename__ = "tb_meta_snaplist"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    uuid = Column(String(64), nullable=False)           # Storage Node UUID
    target_uuid = Column(String(64), nullable=False)    # Target Node UUID (node type uuid)
    nodetype = Column(String(64), nullable=False)       # Node Type (Master, Storage, Compute)
    usetype = Column(String(64), nullable=False)        # ORIGIN, OS, DATA
    name = Column(String(256), nullable=True)
    snapname = Column(String(256), nullable=True)
    pool_property_id = Column(Integer)
    zfs_property_id = Column(Integer)
    pool_data_id = Column(Integer)
    snapshot_data_id = Column(BIGINT)
    iscsiinfo_sub_id = Column(BIGINT)
    boot_data_id = Column(BIGINT)
    islast = Column(Integer, default=1)  # Restore Last Snapshot (0:False, 1: True)
    isfull = Column(Integer, default=0)  # snapshot save filetype (0: increment 1: full)
    ispolicebackup = Column(Integer, default=0)  # police full backup (0: not 1: police backup)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class MetaDataRollback(Base):
    __tablename__ = "tb_meta_snaplist_rollback"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    meta_id = Column(BIGINT, nullable=True)
    uuid = Column(String(64), nullable=False)  # Storage Node UUID
    target_uuid = Column(String(64), nullable=False)  # Target Node UUID (node type uuid)
    nodetype = Column(String(64), nullable=False)  # Node Type (Master, Storage, Compute)
    usetype = Column(String(64), nullable=False)  # ORIGIN, OS, DATA
    name = Column(String(256), nullable=True)
    snapname = Column(String(256), nullable=True)
    pool_property_id = Column(Integer)
    zfs_property_id = Column(Integer)
    pool_data_id = Column(Integer)
    snapshot_data_id = Column(BIGINT)
    boot_data_id = Column(BIGINT)
    iscsiinfo_sub_id = Column(BIGINT)
    islast = Column(Integer, default=1)  # Restore Last Snapshot (0:False, 1: True)
    isfull = Column(Integer, default=0)  # snapshot save filetype (0: increment 1: full)
    ispolicebackup = Column(Integer, default=0) # increment snapfile fullbackup (0: not 1: increment full)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class SnapData(Base):
    __tablename__ = "tb_meta_snapdata"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    dataset = Column(String(256), nullable=False)
    snapname = Column(String(256), nullable=True)
    snapfilename = Column(String(512), nullable=True)
    snapfullname = Column(String(512), nullable=True)
    priv_snapfilename = Column(String(256), nullable=True)
    priv_snapfullname = Column(String(256), nullable=True)
    save_path = Column(String(1024), nullable=True)
    part_path = Column(String(1024), nullable=True)
    isfull = Column(Integer, default=0)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class BootData(Base):
    __tablename__ = "tb_meta_bootdata"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    pool = Column(String(32), nullable=True)
    path = Column(String(512), nullable=True)
    devname = Column(String(32), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class IscsiInfo(Base):
    __tablename__ = "tb_meta_iscsiInfo"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    sub_id = Column(BIGINT)
    lun_id = Column(String(8))
    backend_type = Column(String(8))
    lun_type = Column(String(8))
    size = Column(String(128))
    blocksize = Column(String(8))
    serial_number = Column(String(64))
    device_id = Column(String(32))
    num_threads = Column(String(8))
    file_path = Column(String(1024))
    ctld_name = Column(String(256))
    scsiname = Column(String(256))
    server_uuid = Column(String(64))
    target_uuid = Column(String(64))
    register_dt = Column(DateTime(timezone=True), default=func.now())


