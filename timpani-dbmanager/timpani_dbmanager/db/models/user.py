from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, BIGINT
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql.types import MEDIUMBLOB

from . import Base

class User(Base):       # Master
    __tablename__ = "tb_master_user"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True)
    username = Column(String(64))
    role = Column(String(10), nullable=True)
    password = Column(String(100), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())

class AuthConnInfo(Base):
    __tablename__ = "tb_auth_conn_info"

    id = Column(BIGINT, primary_key=True)
    user_id = Column(BIGINT)
    role = Column(String(10))
    token = Column(MEDIUMBLOB)
    token_expired_tm = Column(DateTime(timezone=True), nullable=True)
    register_dt = Column(DateTime(timezone=True), default=func.now())

__all__ = ['User', 'AuthConnInfo']