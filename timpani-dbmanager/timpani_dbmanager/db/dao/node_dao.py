import uuid
import logging

from datetime import datetime

from .base_dao import BaseDAO
from .ipmi_dao import IpmiDAO
from ..models.node import NodeDetail, Node, SyncNode, SyncVolume
from ..models.ipmi import IpmiConnectInfo

from sqlalchemy.sql import compiler
from sqlalchemy.dialects import mysql
logger = logging.getLogger(__name__)

class SyncNodeDAO(BaseDAO):
    FIELD = ["uuid", "server_uuid", "node_name", "group_id", "group_name", "ipmi_user_id",
             "ipmi_user_password", "bmc_ip", "bmc_ip_subnet_mask", "bmc_mac_addr", "pxe_mac_addr",
             "created_at"]

    INFO_SERVER_UUID = ["node_name", "uuid", "group_id"]

    @staticmethod
    def SyncNodeUpdate(obj, data, database_session):
        field_list = SyncNodeDAO.FIELD
        uuid = data.get('uuid').replace('-', '').upper()
        data['uuid'] = uuid
        if obj is None:
            # insert
            obj = SyncNode()
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)
        else:
            # update
            BaseDAO.update_value(obj, field_list, data)
            BaseDAO.update(obj, database_session)

        return obj.id

    @staticmethod
    def getobj_nodeuuid(uuid, server_uuid, database_session):
        obj = database_session.query(SyncNode).filter(SyncNode.uuid == uuid)
        obj = obj.filter(SyncNode.server_uuid == server_uuid).first()
        if obj is None:
            return None
        return obj

    @staticmethod
    def getobjlist_syncnode(database_session):
        objlist = database_session.query(SyncNode).all()
        return objlist

    @staticmethod
    def getnodelist(database_session):
        FIELD = ["uuid", "server_uuid", "node_name", "group_id", "group_name", "ipmi_user_id",
                 "ipmi_user_password", "bmc_ip", "bmc_ip_subnet_mask", "bmc_mac_addr", "pxe_mac_addr"]
        query = database_session.query(SyncNode.uuid, SyncNode.server_uuid, SyncNode.node_name,
                                     SyncNode.group_id, SyncNode.group_name, SyncNode.ipmi_user_id,
                                     SyncNode.ipmi_user_password, SyncNode.bmc_ip,
                                     SyncNode.bmc_ip_subnet_mask, SyncNode.bmc_mac_addr,
                                     SyncNode.pxe_mac_addr).all()
        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=FIELD)
        else:
            return []
        return res

    @staticmethod
    def getnodetype(data, database_session):
        INFO_FILED = ['nodetype', 'uuid']
        if 'node_uuid' in data:
            uuid = data.get('node_uuid').replace('-', '').upper()
        else:
            uuid = data.get('uuid').replace('-', '').upper()
        isFind = False
        query = database_session.query(SyncNode.node_name, SyncNode.uuid).all()
        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=INFO_FILED)
            for comparedata in res:
                compare_uuid = comparedata.get('uuid')
                if compare_uuid is not None:
                    if compare_uuid.replace('-','').upper().__eq__(uuid):
                        res = {'nodetype':comparedata.get('nodetype')}
                        isFind = True
                        break
            if not isFind:
                return {'nodetype': None}
            return res
        else:
            return {'nodetype': None}

    @staticmethod
    def SyncNodeDel(obj, database_session):
        BaseDAO.delete(obj, database_session)
        return True


class SyncVolumeDAO(BaseDAO):
    FIELD = ["uuid", "name", "server_uuid", "user_uuid", "group_id", "use_type", "size"]

    @staticmethod
    def SyncVolumeUpdate(obj, data, database_session):
        field_list = SyncVolumeDAO.FIELD

        if obj is None:
            # insert
            obj = SyncVolume()
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)
        else:
            # update
            BaseDAO.update_value(obj, field_list, data)
            BaseDAO.update(obj, database_session)

        return obj.id

    @staticmethod
    def getobj_volumeuuid(uuid, server_uuid, user_uuid, database_session):
        obj = database_session.query(SyncVolume).filter(SyncVolume.uuid == uuid)
        obj = obj.filter(SyncVolume.server_uuid == server_uuid)
        obj = obj.filter(SyncVolume.user_uuid == user_uuid)
        obj = obj.first()
        if obj is None:
            return None
        return obj

    @staticmethod
    def getobjlist_syncvolume(database_session):
        objlist = database_session.query(SyncVolume).all()
        return objlist

    @staticmethod
    def getvolumelist(database_session):

        query = database_session.query(SyncVolume.uuid,
                                       SyncVolume.name,
                                       SyncVolume.server_uuid,
                                       SyncVolume.user_uuid,
                                       SyncVolume.group_id,
                                       SyncVolume.use_type,
                                       SyncVolume.size).all()
        if query is not None:
            res = BaseDAO.return_data(query=query, field_list=SyncVolumeDAO.FIELD)
        else:
            return []
        return res

    @staticmethod
    def SyncVolumeDel(obj, database_session):
        BaseDAO.delete(obj, database_session)
        return True


class NodeDAO(BaseDAO):
    @staticmethod
    def resigster_node(data, database_session):
        obj = Node()
        logger.info('register_node [data] : {}'.format(data))
        query = database_session.query(Node).filter(Node.uuid == data.get('node_uuid')).first()
        logger.info('query data : {}'.format(query))
        if query is None:
            field_list = ["uuid", "parent_uuid", "ischild", "node_detail_id", "system_id"]
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)
            res_id = obj.uuid
        else:
            logger.info("query : {}".format(query))
            res_id = query.uuid
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
        if query is None:
            return None
        res = query.__dict__
        del res['_sa_instance_state']

        return res

    @staticmethod
    def update_node(data, database_session):
        field_list = ["uuid", "parent_uuid", "ischild", "node_detail_id", "system_id"]
        obj = database_session.query(Node).filter(Node.uuid == data.get('node_uuid')).first()
        if obj is None:
            return None
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
            res_id = query.id

        return res_id

    @staticmethod
    def get_node_detail_info(data, database_session):
        query = database_session.query(NodeDetail.node_uuid, NodeDetail.alias, NodeDetail.capability, NodeDetail.note,
                                       NodeDetail.register_dt, IpmiConnectInfo.ipv4address).\
                                join(Node, Node.uuid == NodeDetail.node_uuid).\
                                join(IpmiConnectInfo, IpmiConnectInfo.id == NodeDetail.ipmi_conn_id)

        if 'search_kind' in data:
            search_kind = data.get('search_kind')
            if search_kind == 1:    # Get Parent Node
                query = query.filter(NodeDetail.capability.in_(('master', 'storage')))
            elif search_kind == 2:  # Get Child Node
                query = query.filter(NodeDetail.capability.in_(('compute', 'leader')))
                query = query.filter(Node.parent_uuid == data.get('parent_uuid'))

        BaseDAO.debug_sql_print(query=query, func_name='get_node_detail_info')
        query = query.all()
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

__all__ =[SyncNodeDAO, NodeDAO, NodeDetailDAO]
