from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, BIGINT
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql.types import MEDIUMBLOB

from . import Base


class PoliceTableStatus(Base):

    __tablename__ = "tb_police_status"

    id = Column(BIGINT, primary_key=True)
    police_type_code = Column(String(8))   # 00: System, 10: BIOS , 20: Backup, 30: Recover
    police_kind_code = Column(String(8))   # PD : Police Default PS: Police Setting
    police_code = Column(String(8))        # [kind_code]+[type_code]+[police_user_code]
    police_user_id = Column(String(128))
    police_user_code = Column(String(64), unique=True)
    police_target_uuid = Column(String(128))    # PHY UUID
    police_name = Column(String(128))      # Police Name
    police_crontab = Column(String(128))         # Police prioed
    police_last_result = Column(Integer, default=0)  # 0: Not Running 1:Success 2:Failed
    police_last_runtime = Column(DateTime(timezone=True)) # Sync Run Start Time
    register_dt = Column(DateTime(timezone=True), default=func.now())


class PoliceRunHist(Base):

    __tablename__ = "tb_police_his"

    id = Column(BIGINT, primary_key=True)
    police_code = Column(String(128))
    police_name = Column(String(128))
    police_start_at = Column(DateTime(timezone=True))
    police_stop_at = Column(DateTime(timezone=True))
    police_result = Column(String(16))
    police_err_code = Column(String(8))
    police_err_msg = Column(String(128))
    register_dt = Column(DateTime(timezone=True), default=func.now())


__all__ = ['PoliceTableStatus', 'PoliceRunHist']