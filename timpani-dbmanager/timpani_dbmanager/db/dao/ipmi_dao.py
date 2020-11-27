import logging
from .base_dao import BaseDAO
from ..models.ipmi import IpmiConnectInfo
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

class IpmiDAO(BaseDAO):
    @staticmethod
    def register_ipmi_connection_info(data, database_session):
        ipmi_info_data = data.get('ipmi_info')
        result = database_session.query(IpmiConnectInfo).filter(IpmiConnectInfo.node_uuid == data.get('node_uuid')).first()

        if result is None:
            ipmi_info_data['ipv4address'] = ipmi_info_data.get('ipv4addr')
            ipmi_info_data['passwd'] = ipmi_info_data.get('ipv4addr')
            ipmi_info_data['node_uuid'] = data.get('node_uuid')
            field_list = ["ipv4address", "ipv4port", "user", "passwd", "node_uuid", "is_discovery"]
            obj = IpmiConnectInfo()
            BaseDAO.set_value(obj,field_list,ipmi_info_data)
            BaseDAO.insert(obj,database_session)

            return obj.id, obj.node_uuid
        else:
            return None, ''

    @staticmethod # @BaseDAO.database_operation
    def update_ipmi_connection_info(data, database_session):
        field_list = ["ipv4address", "ipv4port", "user", "passwd", "node_uuid", "is_discovery"]
        obj = database_session.query(IpmiConnectInfo).filter(IpmiConnectInfo.node_uuid == data.get('node_uuid')).first()
        BaseDAO.update_value(obj, field_list, data)
        obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod # @BaseDAO.database_operation
    def del_ipmi_connection_info(node_uuid, database_session):
        try:
            data = database_session.query(IpmiConnectInfo).filter(IpmiConnectInfo.node_uuid == node_uuid).first()
            BaseDAO.delete(data,database_session)
        except:
            return '0'
        return '1'

    @staticmethod
    # @BaseDAO.database_operation
    def get_ipmi_connection_id(data, database_session):
        data = database_session.query(IpmiConnectInfo).filter(IpmiConnectInfo.node_uuid == data.get('node_uuid')).first()
        if data is None:
            return None
        return data.id


    @staticmethod
    # @BaseDAO.database_operation
    def get_ipmi_connection_info(ipmi_connection_id, database_session):
        if ipmi_connection_id is 0:
            return [database_session.query(IpmiConnectInfo).all()]
        else:
            return [database_session.query(IpmiConnectInfo).filter(IpmiConnectInfo.id == ipmi_connection_id).all()]

    @staticmethod
    # @BaseDAO.database_operation
    def update_ipmi_connection_node_detail_id(ipmi_connection_id, node_detail_id, database_session):
        database_session.query(IpmiConnectInfo).filter(IpmiConnectInfo.id == ipmi_connection_id).update({IpmiConnectInfo.node_detail_id:node_detail_id})
        # database_session.commit()

    @staticmethod
    # @BaseDAO.database_operation
    def set_ipmi_node_detail(node_detail_id, node_detail_obj, ipmi_connection_id, database_session):
        print("======")
        node_detail_obj_list = [node_detail_obj]
        obj = database_session.query(IpmiConnectInfo).get(ipmi_connection_id) #.filter(IpmiConnectInfo.id == ipmi_connection_id)   #.update({IpmiConnectInfo.node_detail_id:int(node_detail_id)})
        print(type(obj))
        obj.node_detail_id = node_detail_id
        obj.node_detail = node_detail_obj
        # obj.node_detail_id = node_detail_id
        print("======")
        database_session.add(obj)
        database_session.flush()
        database_session.refresh(obj)
        print("======")

        return obj.id


__all__ = [IpmiDAO]