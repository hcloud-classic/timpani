from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, BIGINT
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql.types import MEDIUMBLOB
from timpani_base.db.tabledefind import TB_SYNC_STATUS, TB_SYNC_HIST

from . import Base


class SyncTableStatus(Base):
    __tablename__ = TB_SYNC_STATUS
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    sync_type_code = Column(String(8))   # 10: Master Authorization , 20: Node Data
    sync_kind_code = Column(String(8))   # AU : Authorization DA : Data Sync
    sync_code = Column(String(8))        # [kind_code]+[type_code]
    sync_name = Column(String(128))      # Sync Discription
    sync_delay = Column(Integer)         # second value
    sync_last_result = Column(Integer, default=0)  # 0: Not Running 1:Success 2:Failed
    sync_last_runtime = Column(DateTime(timezone=True), default=func.now())     # Sync Run Start Time


class SyncTableHist(Base):
    __tablename__ = TB_SYNC_HIST
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    sync_type = Column(String(8))
    sync_code = Column(String(8))
    sync_name = Column(String(128))
    sync_start_at = Column(DateTime(timezone=True))
    sync_stop_at = Column(DateTime(timezone=True))
    sync_result = Column(String(16))
    sync_err_code = Column(String(8))
    sync_err_msg = Column(String(128))
    register_dt = Column(DateTime(timezone=True), default=func.now())


__all__ = ['SyncTableStatus', 'SyncTableHist']