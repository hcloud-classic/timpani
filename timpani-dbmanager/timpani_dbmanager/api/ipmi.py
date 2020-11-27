import logging
from timpani_dbmanager.db import dao
from .base import Base
from timpani_dbmanager.db.dao.base_dao import BaseDAO

import uuid

logger = logging.getLogger(__name__)

class IpmiAPI(object):
    base = Base()

    @BaseDAO.database_operation
    def registerIPMIConn(self, data, database_session):
        logger.info('registerIPMIConn {}'.format(data))
        res_data = {}
        data['node_uuid'] = str(uuid.uuid4())
        _, node_uuid = dao.ipmi_dao.IpmiDAO.register_ipmi_connection_info(data, database_session=database_session)
        res_data['nodeuuid'] = str(node_uuid)
        return res_data

    @BaseDAO.database_operation
    def updateIPMIConn(self, data, database_session):
        logger.info('updateIPMIConn {}'.format(data))
        ## conn_id ==> node_uuid
        res_data = {}
        data['node_uuid'] = data.get('conn_id')
        node_uuid = dao.ipmi_dao.IpmiDAO.update_ipmi_connection_info(data, database_session=database_session)
        res_data['nodeuuid'] = str(node_uuid)
        return res_data

    @BaseDAO.database_operation
    def deleteIPMIConn(self, data, database_session):
        logger.info('deleteIPMIConn {}'.format(data))
        res = dao.ipmi_dao.IpmiDAO.del_ipmi_connection_info(node_uuid=data.get('conn_id'), database_session=database_session)
        if res.__eq__('0'):
            return {'result': '0', 'resultmsg': 'Data deletion failure'}
        else:
            return {'result':'1', 'resultmsg':'Data deletion complete'}

