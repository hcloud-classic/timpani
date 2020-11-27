from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, CHAR
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func

from . import Base

def generate_uuid():
    return str(uuid.uuid4())

class Node(Base):
    __tablename__ = "tb_node"

    uuid = Column(String(64), primary_key=True, default=generate_uuid, nullable=False)
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
    ipmi_conn_id = Column(Integer, default=0)
    #node = relationship('Node',uselist=False, backref=backref("node_detail"))
    #ipmi_info = relationship("IpmiConnectInfo", uselist=False, backref=backref("node_detail"))

__all__ = ["Node", "NodeDetail"]
