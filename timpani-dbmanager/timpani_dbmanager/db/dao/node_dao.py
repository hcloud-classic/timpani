import uuid
import logging

from datetime import datetime

from .base_dao import BaseDAO
from .ipmi_dao import IpmiDAO
from ..models.node import NodeDetail, Node
from ..models.ipmi import IpmiConnectInfo
logger = logging.getLogger(__name__)

class NodeDAO(BaseDAO):
    @staticmethod
    def resigster_node(data, database_session):
        obj = Node()
        query = database_session.query(Node).filter(Node.uuid == data.get('node_uuid')).first()

        if query is None:
            field_list = ["uuid", "parent_uuid", "ischild", "node_detail_id", "system_id"]
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)
            res_id = obj.uuid
        else:
            logger.info("query : {}".format(query))
            res_id = query.get('uuid')
        return res_id

    @staticmethod
    def get_node_information(data, database_session):
        query = None
        search_kind = data.get('search_kind')
        if search_kind == 0:
            query = database_session.query(Node).filter(Node.uuid == data.get('node_uuid')).first()
        # elif search_kind == 1:
        # elif search_kind == 2:
        # elif search_kind == 3:
        #     query = database_session.query(Node).filter(Node.id == node_id).all()
        # elif node_uuid:
        #     query = database_session.query(Node).filter(Node.node_uuid == node_uuid).all()
        res = query.__dict__
        del res['_sa_instance_state']

        return res

    @staticmethod
    def update_node(data, database_session):
        field_list = ["uuid", "parent_uuid", "ischild", "node_detail_id", "system_id"]
        obj = database_session.query(Node).filter(Node.uuid == data.get('node_uuid')).first()
        BaseDAO.update_value(obj, field_list, data)
        BaseDAO.update(obj, database_session)
        return obj.uuid


class NodeDetailDAO(BaseDAO):
    @staticmethod
    def resigster_node_detail(data, database_session):

        obj = NodeDetail()

        query = database_session.query(NodeDetail).filter(NodeDetail.node_uuid == data.get('node_uuid')).first()

        if query is None:
            field_list = ['capability', 'capability_code', 'alias', 'used_flag', 'is_monitor', 'node_uuid', 'ipmi_conn_id']
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)
            res_id = obj.id
            field_list = ["uuid", "parent_uuid", "ischild", "node_detail_id", "system_id"]
            node = database_session.query(Node).filter(Node.uuid == data.get('node_uuid')).first()
            node.node_detail_id = obj.id
            BaseDAO.update_value(node, field_list, data)
            BaseDAO.update(node, database_session)
        else:
            res_id = query.get('id')

        return res_id

    @staticmethod
    def get_node_detail_info(data, database_session):
        query = database_session.query(NodeDetail.node_uuid, NodeDetail.alias, NodeDetail.capability, NodeDetail.note, NodeDetail.register_dt,
                                       IpmiConnectInfo.ipv4address).\
                                join(IpmiConnectInfo, IpmiConnectInfo.id == NodeDetail.ipmi_conn_id).all()
        result_templete = {'node_uuid': None, 'node_name': None, 'node_type': None, 'note': None, 'register_dt': None, 'ipmi_address': None}
        field_list = ['node_uuid', 'node_name', 'node_type', 'note', 'register_dt', 'ipmi_address']
        res = []
        if isinstance(query, list):
            logger.info("query list")
            for item in query:
                temp_list = list(item)
                cnt = 0
                temp_res = {}
                for field in field_list:
                    logger.info('type : {}'.format(type(temp_list[cnt])))
                    if isinstance(temp_list[cnt], datetime):
                        temp_list[cnt] = temp_list[cnt].strftime('%Y-%m-%d %H:%M:%S')
                    temp_res[field] = temp_list[cnt]
                    cnt += 1
                logger.info('temp_res : {}'.format(temp_res))
                res.append(temp_res)
        else:
            logger.info("query raw")
        logger.info("[get_node_detail_info : {}, type : {}".format(res, type(res)))

        return res

    @staticmethod
    def get_node_detail_obj(ipmi_connection_id, database_session):
        return database_session.query(NodeDetail).get(ipmi_connection_id)

    @staticmethod
    def get_node_detail(ipmi_connection_id, database_session):
        return database_session.query(NodeDetail)

__all__ =[NodeDAO, NodeDetailDAO]
