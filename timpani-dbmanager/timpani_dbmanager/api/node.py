import logging
from timpani_dbmanager.db import dao
from .base import Base
from timpani_dbmanager.db.dao.base_dao import BaseDAO
from timpani_dbmanager.db.models.node import NodeDetail, Node
logger = logging.getLogger(__name__)

class NodeAPI(object):

    base = Base()

    def check_capability(self, data):
        capability = data.get('capability').upper()
        if capability.__eq__('MASTER'):
            ischild = 0
            capability_code = 'MN'
        elif capability.__eq__('STORAGE'):
            ischild = 0
            capability_code = "SN"
        elif capability.__eq__('LEADER'):
            ischild = 1
            capability_code = "LN"
        elif capability.__eq__('BACKUP'):
            ischild = 0
            capability_code = "BN"
        else:
            ischild = 1
            capability_code = 'CN'

        node_detail_data = {
            'capability': data.get('capability'),
            'capability_code': capability_code,
            'alias': data.get('alias'),
            'used_flag': 1,
            'is_monitor': 1,
            'node_uuid': data.get('node_uuid')
        }

        node_data = {
            'uuid': data.get('node_uuid'),
            'parent_uuid': None,
            'ischild': ischild,
            'system_id': None
        }

        return node_data, node_detail_data

    """
    Interface : IF_WM_TR_001
    """
    @BaseDAO.database_operation
    def registerNode(self, data, database_session):
        logger.info('RegisterNode {}'.format(data))
        # Create IPMI Connection Information
        ipmi_id = dao.ipmi_dao.IpmiDAO.get_ipmi_connection_id(data=data, database_session= database_session)
        if ipmi_id is None:
            ipmi_id, _ = dao.ipmi_dao.IpmiDAO.register_ipmi_connection_info(data=data, database_session=database_session)
        data['capability'] = data.get('node_type')
        data['alias'] = data.get('node_name')
        node_data, node_detail_data = self.check_capability(data)
        node_detail_data['ipmi_conn_id'] = ipmi_id
        node_uuid = dao.node_dao.NodeDAO.resigster_node(node_data, database_session)
        logger.info("registerNode : node_uuid : {}".format(node_uuid))
        # Register Node Detail table
        node_detail_id = dao.node_dao.NodeDetailDAO.resigster_node_detail(node_detail_data, database_session)
        logger.info("registerNode : node_detail_id : {}".format(node_detail_id))

        return {"node_uuid": node_uuid}

    @BaseDAO.database_operation
    def registerSystemNode(self, data, database_session):
        logger.info('RegisterSystemNode {}'.format(data))
        # {'nodeuuid': '9F824D5656C1C83B51991D1DDCB8D5C1', 'capability': 'Leader', 'alias': 'Leader'}
        node_data, node_detail_data = self.check_capability(data)
        node_detail_data['ipmi_conn_id'] = None
        # Register Node table
        node_uuid = dao.node_dao.NodeDAO.resigster_node(node_data, database_session)
        logger.info("registerSystemNode : node_uuid : {}".format(node_uuid))
        # Register Node Detail table
        node_detail_id = dao.node_dao.NodeDetailDAO.resigster_node_detail(node_detail_data, database_session)
        logger.info("registerSystemNode : node_detail_id : {}".format(node_detail_id))
        node_data['node_detail_id'] = node_detail_id

        return data

    # All Node List
    @BaseDAO.database_operation
    def getNodeList(self, data, database_session):
        res = dao.node_dao.NodeDetailDAO.get_node_detail_info(data=data, database_session= database_session)
        res_data = {'node_info': res}
        logger.info("getNodeList {}".format(res))
        return res_data

    # Leader Node List
    @BaseDAO.database_operation
    def getNodeLeaderList(self, data, database_session):
        logger.info("getNodeLeaderList {}".format(data))
        return {"uuid": "getNodeLeaderList"}

    # Compute Node List
    @BaseDAO.database_operation
    def getNodeComputeList(self, data, database_session):
        logger.info("getNodeComputeList nodeuuid : {}".format(data.get('node_uuid')))
        res = "\"getNodeComputeList nodeuuid : {}\"".format(data.get('node_uuid'))
        return {"uuid": res}

    # Get Node Info
    @BaseDAO.database_operation
    def getNodeInfo(self, data, database_session):
        logger.info("getNodeInfo nodeuuid : {}".format(data.get('node_uuid')))
        search_data = {'nodeuuid': data.get('node_uuid'), 'search_kind': 0}
        res = dao.node_dao.NodeDAO.get_node_information(search_data, database_session=database_session)
        print(res)
        return res

    # Updete Node
    @BaseDAO.database_operation
    def updateNode(self, data, database_session):
        logger.info("updateNode: nodeuuid : {}".format(data.get('node_uuid')))
        res = "\"updateNode: nodeuuid : {}\"".format(data.get('node_uuid'))
        return {"uuid": res}

    # Delete Node Info
    @BaseDAO.database_operation
    def deleteNode(self, data, database_session):
        logger.info("deleteNode nodeuuid : {}".format(data.get('node_uuid')))
        res = "\"deleteNode nodeuuid : {}\"".format(data.get('node_uuid'))
        return {"uuid": res}