from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, CHAR
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy import select

from . import Base




class Bios(Base):
    __tablename__ = "tb_bios"


    id = Column("id", Integer, primary_key=True)
    node_uuid = Column(String(64))
    bios_version = Column(String(128), nullable=True)
    firmware_version = Column(String(32), nullable=True)

class BiosConfigHistory(Base):
    __tablename__ = "tb_bios_hist"

    id = Column("id", Integer, primary_key=True)
    bios_id = Column(Integer)
    node_uuid = Column(String(64))
    kind = Column(String(32), nullable=False)
    kind_code = Column(String(32))
    bios_version = Column(String(128), nullable=True)
    firmware_version = Column(String(32), nullable=True)
    result = Column(String(32))
    result_code = Column(String(32))
    error = Column(String(256))
    error_code = Column(String(32))
    register_dt = Column(DateTime(timezone=True), default=func.now())

    # bios = relationship("Bios", back_populates="config_cur", uselist=False)     # 1:1 relationship
    # config_id = Column(Integer, ForeignKey('tb_bios_config.id'))
    # config = relationship("BiosConfig", back_populates="config_cur")


class BiosConfig(Base):
    __tablename__ = "tb_bios_config"

    id = Column("id", Integer, primary_key=True)
    node_uuid = Column(String(64))
    bios_id = Column(Integer)
    isdefault = Column(Integer, default=0, nullable=False)
    iscurrent = Column(Integer, default=0, nullable=False)
    config_list_id = Column(Integer)
    register_dt = Column(DateTime(timezone=True), default=func.now())

    # config_cur = relationship("BiosConfigCurrent", back_populates="config", uselist=False)  # 1:1 relationship
    # sections = relationship("BiosSections", back_populates="config_cur")


class BiosConfigList(Base):
    __tablename__ = "tb_bios_config_list"

    id = Column("id", Integer, primary_key=True)
    list_cnt = Column(Integer, default=0, nullable=False)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class BiosOptions(Base):
    __tablename__ = "tb_bios_config_options"

    id = Column("id", Integer, primary_key=True)
    # section = relationship("BiosSections", back_populates="options")
    config_list_id = Column(Integer)
    section_key = Column(String(256), nullable=False)
    key = Column(String(256), nullable=True)
    value = Column(String(256), nullable=True)
    viewtype = Column(String(32), nullable=True)
    avail_list_id = Column(Integer)

class BiosOptionsAvailList(Base):
    __tablename__ = "tb_bios_config_avail_list"

    id = Column("id", Integer, primary_key=True)
    list_cnt = Column(Integer, default=0, nullable=False)


class BiosOptionsAvail(Base):
    __tablename__ = "tb_bios_config_avail"

    id = Column("id", Integer, primary_key=True)
    avail_list_id = Column(Integer, nullable=False)
    key = Column(String(128), nullable=False)
    key_id = Column(String(128), nullable=True)



__all__ = ['Bios',
           'BiosConfig',
           'BiosConfigList',
           'BiosConfigHistory',
           'BiosOptions',
           'BiosOptionsAvailList',
           'BiosOptionsAvail'
        ]