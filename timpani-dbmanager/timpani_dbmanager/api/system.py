import logging
from timpani_dbmanager.db import dao
from .base import Base
from timpani_dbmanager.db.dao.base_dao import BaseDAO

import uuid

logger = logging.getLogger(__name__)

class SystemAPI(object):
    base = Base()

    @BaseDAO.database_operation
    def registerAgent(self, data, database_session):
        logger.info('registerAgent {}'.format(data))
        res_data = {}
        agent_uuid = dao.system_dao.agentDAO.registerAgent(data, database_session=database_session)
        res_data['agent_id'] = agent_uuid
        return res_data

    @BaseDAO.database_operation
    def registerSystemInfo(self, data, database_session):
        """
        Create tb_system Table
        :param data:
        :param database_session:
        :return:
        """
        logger.info('registerSystemInfo {}'.format(data))
        res_data = {}
        system_id = dao.system_dao.systemDAO.getSystemID(data, database_session=database_session)

        if system_id is None:
            if data.get('os_type').upper().__eq__('LINUX'):
                data['os_type_code'] = 'TO01'
            else:
                data['os_type_code'] = 'TO02'
            if data.get('os_arch').upper().__eq__('X86_64'):
                data['os_arch_code'] = 'AO01'
            else:
                data['os_arch_code'] = 'AO02'
            system_id, node_uuid = dao.system_dao.systemDAO.registerSystem(data, database_session=database_session)
            node_data = {}
            node_data['system_id'] = system_id
            node_data['nodeuuid'] = node_uuid
            node_uuid = dao.node_dao.NodeDAO.update_node(node_data, database_session=database_session)
            logging.info("node_uuid : {}".format(node_uuid))
        else:
            logger.info('Exist System ID : node_uuid : {}'.format(data.get('node_uuid')))

        res_data['system_id'] = system_id
        return res_data


