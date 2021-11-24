from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, BIGINT
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql.types import MEDIUMBLOB

from . import Base

class App(Base):
    __tablename__ = "tb_app_info"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    uuid = Column(String(64))
    nodetype = Column(String(16))
    ipaddress = Column(String(32))
    macaddress = Column(String(64))
    register_dt = Column(DateTime(timezone=True), default=func.now())

class ModuleStatus(Base):

    __tablename__ = "tb_app_module_status"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    pid = Column(String(8))
    modulename = Column(String(32))
    moduletype = Column(String(128))
    start_at = Column(DateTime(timezone=True))
    check_at = Column(DateTime(timezone=True))
    appinfo_id = Column(BIGINT)


class TimpaniConfig(Base):

    __tablename__ = "tb_timpani_config"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    rabbit_id = Column(String(32))
    rabbit_pass = Column(String(32))
    rabbit_port = Column(String(8))
    backup_ip = Column(String(32))
    backup_nic = Column(String(32))
    master_nic = Column(String(32))
    storage_nic = Column(String(32))
    ipmimanager_nic = Column(String(32))
    master_data_prefix = Column(String(128))
    storage_data_prefix = Column(String(128))
    nfs_export_path = Column(String(256))
    nfs_mount_path = Column(String(256))
    osbackup_api_ip = Column(String(32))
    osbackup_api_port = Column(String(32))
    register_dt = Column(DateTime(timezone=True), default=func.now())

class DataDir(Base):
    __tablename__ = "tb_data_dircollect"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    uuid = Column(String(64))
    usetype = Column(String(32))
    modulename = Column(String(64))
    name = Column(String(64))
    nodetype = Column(String(32))

__all__ = ['App', 'SyncTableStatus', 'TimpaniConfig']

