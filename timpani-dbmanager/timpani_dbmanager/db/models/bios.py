from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, BIGINT
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

class BiosRedfishAvail(Base):
    __tablename__ = "tb_redfish_avail"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    redfish_key = Column(String(64))
    cfg_set_val = Column(String(64))
    redfish_val = Column(Integer)

class BiosRedfishMatch(Base):
    __tablename__ = "tb_redfish_match"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    redfish_key = Column(String(64))
    syscfg_key = Column(String(128))
    match_kind = Column(String(64))


class BiosTemplate(Base):
    __tablename__ = "tb_bios_template"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    redfish_key = Column(String(64))
    name = Column(String(64))
    redfish_val = Column(Integer)
    cfg_set_val = Column(String(64))

class BiosCurBiosconfig(Base):
    __tablename__ = "tb_bios_cur_biosconfig"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    sub_id = Column(BIGINT)
    macaddr = Column(String(64))
    guid = Column(String(64))
    section = Column(String(256))
    syscfg_key = Column(String(256))
    cfg_set_val = Column(String(64))
    register_dt = Column(DateTime(timezone=True), default=func.now())

class BiosCurTemplate(Base):
    __tablename__ = "tb_bios_cur_template"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    macaddr = Column(String(64))
    guid = Column(String(64))
    name = Column(String(32))
    redfish_key = Column(String(64))
    syscfg_key = Column(String(128))
    match_kind = Column(String(64))
    cfg_set_val = Column(String(64))
    redfish_val = Column(Integer)
    cfg_bios_ver = Column(String(64))
    cfg_fw_opcode = Column(String(64))
    register_dt = Column(DateTime(timezone=True), default=func.now())

class BiosBackup(Base):
    __tablename__ = "tb_bios_backup"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    macaddr = Column(String(64))
    guid = Column(String(64))
    kind = Column(String(16))
    backupname = Column(String(64))
    sys_bios_ver = Column(String(64))
    sys_me_ver = Column(String(64))
    sys_sdr_ver = Column(String(64))
    sys_bmc_ver = Column(String(64))
    template_name = Column(String(64))
    syscfg_path = Column(String(256))
    syscfg_filename = Column(String(128))
    redfish_filename = Column(String(128))
    syscfg_sub_id = Column(BIGINT)
    register_dt = Column(DateTime(timezone=True), default=func.now())


__all__ = ['Bios',
           'BiosConfig',
           'BiosConfigList',
           'BiosConfigHistory',
           'BiosOptions',
           'BiosOptionsAvailList',
           'BiosOptionsAvail',
           'BiosRedfishAvail',
           'BiosRedfishMatch',
           'BiosTemplate'
        ]