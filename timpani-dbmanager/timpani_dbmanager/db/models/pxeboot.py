from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, CHAR
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func

from . import Base

class PxebootImage(Base):
    __tablename__ = "tb_pxeboot_image"

    id = Column(Integer, primary_key=True)
    os_type = Column(String(32))
    os_type_code = Column(String(32))
    os_version = Column(String(32))
    os_arch = Column(String(32))
    os_arch_code = Column(String(32))
    label = Column(String(128))
    repo_name = Column(String(256))
    vmlinuz_path = Column(String(256))
    initrd_path = Column(String(256))
    image_file_path = Column(String(256))
    image_file_name= Column(String(256))
    target = Column(String(32))
    target_code = Column(String(32))
    register_dt = Column(DateTime(timezone=True), default=func.now())

class Pxeboot(Base):
    __tablename__ = "tb_pxeboot"

    id = Column(Integer, primary_key=True)
    ismount = Column(Integer, default=0)        # 0: not mounted 1: mounted
    isdefault = Column(Integer, default=0)      # 0: no default  1: default
    mount_path = Column(String(256), nullable=True)    # image mount path
    image_id = Column(Integer)

class PxebootHist(Base):
    __tablename__ = "tb_pxeboot_hist"

    id = Column(Integer, primary_key=True)
    os_type = Column(String(32))
    os_type_code = Column(String(32))
    os_version = Column(String(32))
    os_arch = Column(String(32))
    os_arch_code = Column(String(32))
    label = Column(String(128))
    target = Column(String(32))
    target_code = Column(String(32))
    action = Column(String(64))
    action_code = Column(String(32))
    result = Column(String(32))
    result_code = Column(String(32))
    error = Column(String(256))
    error_code = Column(String(32))
    register_dt = Column(DateTime(timezone=True), default=func.now())

__all__ = [ 'PxebootImage' , 'Pxeboot', 'PxebootHist' ]