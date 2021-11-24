from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, BIGINT
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func

from . import Base

def generate_uuid():
    return str(uuid.uuid4())

class Node(Base):
    __tablename__ = "tb_node"

    uuid = Column(String(64), primary_key=True, nullable=False)
    parent_uuid = Column(String(64))
    # parent = relationship("Node", backref=backref("child"))
    ischild = Column(Integer, default=0, nullable=False)                # 0:Flase, 1: True
    node_detail_id = Column(Integer)
    # node_detail = relationship("NodeDetail", backref=backref("node"))
    # bios = relationship("Bios", backref=backref("node"))
    system_id = Column(Integer)
    # system = relationship("System", backref=backref("node"))
    # node_detail = relationship("NodeDetail",uselist=True, backref=backref("node"))


class NodeDetail(Base):
    __tablename__ = "tb_node_detail"

    id = Column(Integer, primary_key=True)
    capability = Column(String(32))
    capability_code = Column(String(32))
    alias = Column(String(32))
    register_dt = Column(DateTime(timezone=True), default=func.now())
    used_flag = Column(Integer)
    is_monitor = Column(Integer)
    node_uuid = Column(String(64))
    note = Column(String(256))
    service_macaddress = Column(String(64), nullable=True)
    ipmi_conn_id = Column(Integer, default=0)
    #node = relationship('Node',uselist=False, backref=backref("node_detail"))
    #ipmi_info = relationship("IpmiConnectInfo", uselist=False, backref=backref("node_detail"))

class SyncNode(Base):
    __tablename__ = "tb_sync_node"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    uuid = Column(String(64))  # phy UUID
    server_uuid = Column(String(64))    # Innogrid Service UUID
    node_name = Column(String(10))  # Parent(MASTER, STORAGE), Child(COMPUTE)
    group_id = Column(String(10))
    group_name = Column(String(64))
    ipmi_user_id = Column(String(64))
    ipmi_user_password = Column(String(300))
    bmc_ip = Column(String(32))
    bmc_ip_subnet_mask = Column(String(32))
    bmc_mac_addr = Column(String(128))
    pxe_mac_addr = Column(String(128))
    created_at = Column(String(128))
    register_dt = Column(DateTime(timezone=True), default=func.now())


class SyncVolume(Base):
    __tablename__ = "tb_sync_volume"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    uuid = Column(String(64))  # Volume UUID
    name = Column(String(128))      # ZFS VOLUME NAME
    server_uuid = Column(String(64))    # Innogrid Service UUID
    user_uuid = Column(String(10))  # USER ID
    group_id = Column(Integer)
    use_type = Column(String(64))
    size = Column(BIGINT)
    register_dt = Column(DateTime(timezone=True), default=func.now())


class TimpaniNode(Base):
    __tablename__ = "tb_timpani_node"

    id = Column(BIGINT, primary_key=True)
    uuid = Column(String(64), unique=True)
    type = Column(String(10))  # Parent(MASTER, STORAGE), Child(COMPUTE)
    groupid = Column(String(10))
    userid = Column(String(64))
    ipmi_user = Column(String(64))
    ipmi_pass = Column(String(100))
    ipmi_ipv4 = Column(String(32))
    ipmi_mac = Column(String(64))
    ipmi_port = Column(String(10))
    register_dt = Column(DateTime(timezone=True), default=func.now())

class ParentNode(Base):
    __tablename__ = "tb_parent_node"

    id = Column(BIGINT, primary_key=True)
    uuid = Column(String(64), unique=True)
    type = Column(String(10))                   # Parent(MASTER, STORAGE), Child(COMPUTE)
    ipmi_user = Column(String(64))
    ipmi_pass = Column(String(100))
    ipmi_ipv4 = Column(String(32))
    ipmi_mac = Column(String(64))
    ipmi_port = Column(String(10))
    register_dt = Column(DateTime(timezone=True), default=func.now())

class ChildNode(Base):
    __tablename__ = "tb_child_node"

    id = Column(BIGINT, primary_key=True)
    uuid = Column(String(64), unique=True)
    type = Column(String(10))                   # Parnet(MASTER, STORAGE), Child(COMPUTE)
    ipmi_user = Column(String(64))
    ipmi_pass = Column(String(100))
    ipmi_ipv4 = Column(String(32))
    ipmi_mac = Column(String(64))
    ipmi_port = Column(String(10))
    register_dt = Column(DateTime(timezone=True), default=func.now())

class ParentChildNode(Base):
    __tablename__ = "tb_parnet_child_node"

    id = Column(BIGINT, primary_key=True)
    parent_uuid = Column(String(64))
    child_uuid = Column(String(64))


__all__ = ['Node', 'NodeDetail', 'ParentNode', 'ChildNode', 'ParentChildNode', 'SyncVolume', 'SyncNode']
