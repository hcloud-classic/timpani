from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, CHAR
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from . import Base

class FirmwareImage(Base):
    __tablename__ = "tb_firmware_image"

    id = Column("id", Integer, primary_key=True)
    bios_id = Column(Integer)
    fw_file_name = Column(String(128), nullable=True)
    fw_file_path = Column(String(256), nullable=True)
    fw_type = Column(String(32), nullable=True)
    fw_type_code = Column(String(32), nullable=True)
    fw_version = Column(String(64), nullable=True)
    product_name = Column(String(256), nullable=True)
    product_code = Column(String(64), nullable=True)
    vendor = Column(String(64), nullable=True)
    release_day = Column(String(32), nullable=True)
    package_kind = Column(String(32), nullable=True)
    package_kind_code = Column(String(32), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class FirmwareDepandency(Base):
    __tablename__ = "tb_firmware_depandency"

    id = Column("id", Integer, primary_key=True)
    image_id = Column(Integer)

    fw_type = Column(String(32), nullable=True)
    fw_type_code = Column(String(32), nullable=True)
    fw_version = Column(String(64), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class FirmwareDepandencyHW(Base):
    __tablename__ = "tb_firmware_depandency_hw"

    id = Column("id", Integer, primary_key=True)
    image_id = Column(Integer)
    product_name = Column(String(256), nullable=True)
    product_code = Column(String(64), nullable=True)
    vendor = Column(String(64), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class FirmwareHist(Base):
    __tablename__ = "tb_firmware_hist"

    id = Column("id", Integer, primary_key=True)
    node_uuid = Column(String(64))
    fw_type = Column(String(32), nullable=True)
    fw_type_code = Column(String(32), nullable=True)
    fw_version = Column(String(64), nullable=True)
    product_name = Column(String(256), nullable=True)
    product_code = Column(String(64), nullable=True)
    vendor = Column(String(64), nullable=True)
    release_day = Column(String(32), nullable=True)
    package_kind = Column(String(32), nullable=True)
    package_kind_code = Column(String(32), nullable=True)
    action = Column(String(64))
    action_code = Column(String(32))
    result = Column(String(32))
    result_code = Column(String(32))
    error = Column(String(256))
    error_code = Column(String(32))
    register_dt = Column(DateTime(timezone=True), default=func.now())

__all__ = [ 'FirmwareImage', 'FirmwareDepandency', 'FirmwareDepandencyHW', 'FirmwareHist' ]
