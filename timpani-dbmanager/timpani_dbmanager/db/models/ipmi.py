from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from . import Base

class IpmiConnectInfo(Base):
    __tablename__ = "tb_ipmi_connect_info"

    id = Column("id", Integer, primary_key=True)
    ipv4address = Column("ipv4address", String(32))
    ipv4port = Column("ipv4port", String(16))
    user = Column("users",String(32))
    passwd = Column("passwd",String(256))
    macaddress = Column(String(64), default='-', nullable=True)
    node_uuid = Column(String(64), nullable=True)       # GET IPMI Data (ipmitool mc guid)
    is_discovery = Column("is_discovery", Integer, default=0)       # 1: true, 0 : false
    register_dt = Column(DateTime(timezone=True), default=func.now())
    update_dt = Column(DateTime(timezone=True), default=func.now())

class IpmiSensor(Base):
    __tablename__ = "tb_ipmi_sensor"

    id = Column("id", Integer, primary_key=True)
    sensor_name = Column(String(128))
    sensor_value = Column(String(128))
    sensor_units = Column(String(128))
    sensor_state = Column(String(64))
    # Valid thresholds
    sensor_lo_norec = Column(String(128))           # Lower Non-Recoverable
    sensor_lo_crit = Column(String(128))            # Lower Critical
    sensor_lo_nocrit = Column(String(128))          # Lower Non-Critical
    sensor_up_nocrit = Column(String(128))          # Upper Non-Critical
    sensor_up_crit = Column(String(128))            # Upper Critical
    sensor_up_norec = Column(String(128))           # Upper None-Recoverable
    register_dt = Column(DateTime(timezone=True), default=func.now())

class IpmiSdrType(Base):
    __tablename__ = "tb_ipmi_sdrtype"

    id = Column("id", Integer, primary_key=True)
    sdr_type_name = Column(String(128))
    sdr_type_code = Column(String(128))
    sensor_name = Column(String(128))
    sensor_divice_code =  Column(String(8))
    register_dt = Column(DateTime(timezone=True), default=func.now())

class IpmiEvent(Base):
    __tablename__ = "tb_ipmi_event"

    id = Column("id", Integer, primary_key=True)
    event_id = Column(String(32))
    event_day = Column(String(128))
    event_time = Column(String(128))
    sensor_type = Column(String(64))
    sensor_divice_code = Column(String(8))
    sensor_event = Column(String(64))
    sensor_evnet_result = Column(String(32))
    register_dt = Column(DateTime(timezone=True), default=func.now())


__all__= [IpmiConnectInfo]