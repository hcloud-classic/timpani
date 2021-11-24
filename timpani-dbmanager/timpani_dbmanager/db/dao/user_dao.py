import uuid
import logging

from datetime import datetime

from .base_dao import BaseDAO
from ..models.user import User

from sqlalchemy.sql import compiler
from sqlalchemy.dialects import mysql

logger = logging.getLogger(__name__)

############################################# [ USER ] #########################################
class UserDAO(BaseDAO):
    
    FIELD = ["username", "role", "password"]
    FIND_KEY = "username"
    INFO_FILED = ["username", "password", "role", "register_dt"]

    @staticmethod
    def register_user(data, database_session):
        field_list = UserDAO.FIELD
        obj = UserDAO.search_equl_data(data.get(UserDAO.FIND_KEY), database_session)
        if obj is None:
            obj = User()
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)
        else:
            BaseDAO.update_value(obj, field_list, data)
            BaseDAO.update(obj, database_session)

        return obj.id

    @staticmethod
    def search_equl_data(username, database_session):
        obj = database_session.query(User).filter(User.username == username).first()
        if obj is None:
            return None
        return obj
    
    @staticmethod
    def get_userinfo(data, database_session):
        query = database_session.query(User.username, User.password, User.role, User.register_dt)
        if data.get(UserDAO.FIND_KEY) is None:        # Find ALL User
            query = query.all()
        else:                           # Find User
            query = query.filter(User.id_name == data.get(UserDAO.FIND_KEY)).first()
        res = BaseDAO.return_data(query=query, field_list=UserDAO.INFO_FILED)

        return res

    @staticmethod
    def get_masterinfo(data, database_session):
        query = database_session.query(User.username, User.password, User.role, User.register_dt)
        query = query.filter(User.role == "MASTER").all()
        res = BaseDAO.return_data(query=query, field_list=UserDAO.INFO_FILED)

        return res

    @staticmethod
    def update_user(data, database_session):
        field_list = UserDAO.FIELD
        obj = UserDAO.search_equl_data(data.get(UserDAO.FIND_KEY), database_session)
        if obj is None:
            return None
        BaseDAO.update_value(obj, field_list, data)
        BaseDAO.update(obj, database_session)
        return obj.id

    @staticmethod
    def delete_user(data, database_session):
        try:
            data = UserDAO.search_equl_data(data.get(UserDAO.FIND_KEY), database_session)
            if data is None:
                return '0'
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'