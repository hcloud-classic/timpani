import logging
from timpani_dbmanager.db import dao
from .base import Base
from timpani_dbmanager.db.dao.base_dao import BaseDAO

import uuid

logger = logging.getLogger(__name__)

class UserAPI(object):
    base = Base()

    # @BaseDAO.database_operation
    # def registerUserManagerNodeList(self, data, database_session):
    #     logger.info('registerUserManagerNodeList {}'.format(data))
    #     res_data = dao.user_dao.UserManagerNodeListDAO.register_usermanagernodelist(data, database_session=database_session)
    #     return res_data
    #
    # @BaseDAO.database_operation
    # def getUserManagerNodeList(self, data, database_session):
    #     logger.info('getUserManagerNodeList {}'.format(data))
    #     res_data = dao.user_dao.UserManagerNodeListDAO.getManagernodelist(data, database_session=database_session)
    #     return res_data

    @BaseDAO.database_operation
    def masteradd(self, data, database_session):
        logger.info('[masteradd] data : {}'.format(data))
        # data['id_name'] = data.get('username')
        data['role'] = "MASTER"
        res_data = dao.user_dao.UserDAO.register_user(data, database_session=database_session)
        return res_data

    @BaseDAO.database_operation
    def getmasterinfo(self, data, database_session):
        logger.info('[GET MASTER INFO] data:{}'.format(data))
        if data is None:
            data = {'username': 'root'}
        res_data = dao.user_dao.UserDAO.get_masterinfo(data, database_session=database_session)
        return res_data


