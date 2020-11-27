import logging
from .base_dao import BaseDAO
from ..models.bios import (Bios, BiosConfig, BiosConfigHistory, BiosConfigList, BiosOptions, BiosOptionsAvail, BiosOptionsAvailList)
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)


########################################## [tb_bios] #######################################################
class BiosDAO(BaseDAO):
    @staticmethod
    def register_bios(data, database_session):
        query = database_session.query(Bios).filter(Bios.node_uuid == data.get('node_uuid')).first()

        if query is None:
            obj = Bios()
            field_list = ["node_uuid", "bios_version", "firmware_version"]
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)

        return obj.id, obj.node_uuid

    """
    check_bios_table
    'tb_bios' table exist : True
    'tb_bios' table not exist : False
    """
    @staticmethod
    def check_bios_table(data, database_session):
        query = database_session.query(Bios).filter(Bios.node_uuid == data.get('node_uuid')).first()
        if query is None:
            return False
        else:
            return True


    @staticmethod  # @BaseDAO.database_operation
    def update_bios(data, database_session):
        obj = database_session.query(Bios).filter(Bios.node_uuid == data.get('node_uuid')).first()
        field_list = ["node_uuid", "bios_version", "firmware_version"]
        BaseDAO.update_value(obj, field_list, data)
        obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid


    @staticmethod  # @BaseDAO.database_operation
    def del_bios(data, database_session):
        try:
            data = database_session.query(Bios).filter(Bios.node_uuid == data.get('node_uuid')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'


class BiosConfigHistDAO(BaseDAO):
    @staticmethod
    def register_biosconfighist(data, database_session):
        list = database_session.query(BiosConfigHistory).filter(BiosConfigHistory.node_uuid == data.get('node_uuid')).all()
        logger.info("list size : {} === {}".format(len(list), list))
        if len(list) != 0:
            return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = BiosConfigHistory()
        field_list = ["bios_id", "node_uuid", "kind", "kind_code", "bios_version",
                      "firmware_version", "result", "result_code", "error", "error_code"
                     ]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.node_uuid


    @staticmethod  # @BaseDAO.database_operation
    def update_biosconfighist(data, database_session):
        obj = database_session.query(BiosConfigHistory).filter(BiosConfigHistory.node_uuid == data.get('node_uuid')).first()
        field_list = ["bios_id", "node_uuid", "kind", "kind_code", "bios_version",
                      "firmware_version", "result", "result_code", "error", "error_code"
                      ]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid


    @staticmethod  # @BaseDAO.database_operation
    def del_biosconfighist(data, database_session):
        try:
            data = database_session.query(BiosConfigHistory).filter(BiosConfigHistory.node_uuid == data.get('node_uuid')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'
#
# class BiosConfig(Base):
#     __tablename__ = "tb_bios_config"
#
#     id = Column("id", Integer, primary_key=True)
#     node_uuid = Column(CHAR(32), ForeignKey('tb_node.uuid'))
#     bios_id = Column(Integer, ForeignKey('tb_bios.id'))
#     isdefault = Column(Integer, default=0, nullable=False)
#     iscurrent = Column(Integer, default=0, nullable=False)
#     config_list_id = Column(Integer, ForeignKey('tb_bios_config_list.id'))
#     register_dt = Column(DateTime(timezone=True), default=func.now())
#
#     # config_cur = relationship("BiosConfigCurrent", back_populates="config", uselist=False)  # 1:1 relationship
#     # sections = relationship("BiosSections", back_populates="config_cur")

class BiosConfigDAO(BaseDAO):
    @staticmethod
    def register_biosconfig(data, database_session):
        list = database_session.query(BiosConfig).filter(
            BiosConfig.node_uuid == data.get('node_uuid')).all()
        logger.info("list size : {} === {}".format(len(list), list))
        if len(list) != 0:
            return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = BiosConfig()
        field_list = ["node_uuid", "bios_id", "isdefault", "iscurrent", "config_list_id"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id, obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def update_biosconfig(data, database_session):
        obj = database_session.query(BiosConfig).filter(
            BiosConfig.node_uuid == data.get('node_uuid')).first()
        field_list = ["node_uuid", "bios_id", "isdefault", "iscurrent", "config_list_id"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def del_biosconfig(data, database_session):
        try:
            data = database_session.query(BiosConfig).filter(
                BiosConfig.node_uuid == data.get('node_uuid')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'

# class BiosConfigList(Base):
#     __tablename__ = "tb_bios_config_list"
#
#     id = Column("id", Integer, primary_key=True)
#     list_cnt = Column(Integer, default=0, nullable=False)
#     register_dt = Column(DateTime(timezone=True), default=func.now())
class BiosConfigListDAO(BaseDAO):
    @staticmethod
    def register_biosconfiglist(data, database_session):
        if not isinstance(data.get('list_id'), type(None)):
            list = database_session.query(BiosConfigList).filter(
                BiosConfigList.id == data.get('list_id')).all()
            logger.info("list size : {} === {}".format(len(list), list))
            if len(list) != 0:
                return {'errorcode': 'E0101', 'errorstr': 'Exist Data'}

        obj = BiosConfigList()
        field_list = ["list_cnt"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod  # @BaseDAO.database_operation
    def del_biosconfiglist(data, database_session):
        try:
            data = database_session.query(BiosConfigList).filter(
                BiosConfigList.id == data.get('list_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'

#
# class BiosOptions(Base):
#     __tablename__ = "tb_bios_config_options"
#
#     id = Column("id", Integer, primary_key=True)
#     # section = relationship("BiosSections", back_populates="options")
#     config_list_id = Column(Integer, ForeignKey('tb_bios_config_list.id'))
#     section_key = Column(String(256), nullable=False)
#     key = Column(String(256), nullable=True)
#     value = Column(String(256), nullable=True)
#     viewtype = Column(String(32), nullable=True)
#     avail_list_id = Column(Integer, ForeignKey('tb_bios_config_avail_list.id'))
class BiosOptionsDAO(BaseDAO):
    @staticmethod
    def register_biosoptions(data, database_session):
        obj = BiosOptions()
        field_list = ["section_key", "key", "value", "viewtype", "config_list_id", "avail_list_id"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod  # @BaseDAO.database_operation
    def update_biosoptions(data, database_session):
        obj = database_session.query(BiosOptions).filter(
            BiosOptions.config_list_id == data.get('config_list_id')).first()
        field_list = ["section_key", "key", "value", "viewtype", "config_list_id", "avail_list_id"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def del_biosoptions(data, database_session):
        try:
            data = database_session.query(BiosOptions).filter(
                BiosConfig.config_list_id == data.get('config_list_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'
#
# class BiosOptionsAvailList(Base):
#     __tablename__ = "tb_bios_config_avail_list"
#
#     id = Column("id", Integer, primary_key=True)
#     list_cnt = Column(Integer, default=0, nullable=False)
class BiosOptionsAvailListDAO(BaseDAO):
    @staticmethod
    def register_biosoptionsavaillist(data, database_session):
        obj = BiosOptionsAvailList()
        field_list = ["list_cnt"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod  # @BaseDAO.database_operation
    def del_biosoptionsavaillist(data, database_session):
        try:
            data = database_session.query(BiosOptionsAvailList).filter(
                BiosOptionsAvailList.id == data.get('list_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'

#
# class BiosOptionsAvail(Base):
#     __tablename__ = "tb_bios_config_avail"
#
#     id = Column("id", Integer, primary_key=True)
#     avail_list_id = Column(Integer, ForeignKey('tb_bios_config_avail_list.id'), nullable=False)
#     key = Column(String(128), nullable=False)
#     key_id = Column(String(128), nullable=True)
class BiosOptionsAvailDAO(BaseDAO):
    @staticmethod
    def register_biosoptionsavail(data, database_session):
        logger.info("[register_biosoptionsavail : {}".format(data))
        obj = BiosOptionsAvail()
        field_list = ["key", "key_id", "avail_list_id"]
        BaseDAO.set_value(obj, field_list, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def check_avail_data(data, database_session):
        subquery = database_session.query(func.count(BiosOptionsAvail.avail_list_id).label('cnt'), BiosOptionsAvail.avail_list_id).\
            group_by(BiosOptionsAvail.avail_list_id).subquery()
        query = database_session.query(func.count(BiosOptionsAvail.avail_list_id), subquery.c.cnt, BiosOptionsAvail.avail_list_id).\
                                        filter(BiosOptionsAvail.key.in_(data.get('in_data'))).\
                                        filter(subquery.c.avail_list_id == BiosOptionsAvail.avail_list_id).group_by(BiosOptionsAvail.avail_list_id).all()
        logger.info("result : {}".format(query))
        if isinstance(query, list):
            for cnt, total_cnt, list_id in query:
                if cnt == total_cnt:
                    return True, list_id

        return False, 0

    @staticmethod  # @BaseDAO.database_operation
    def update_biosoptionsavail(data, database_session):
        obj = database_session.query(BiosOptionsAvail).filter(
            BiosOptionsAvail.avail_list_id == data.get('avail_list_id')).first()
        field_list = ["key", "key_id", "avail_list_id"]
        BaseDAO.update_value(obj, field_list, data)
        # obj.update_dt = func.now()
        BaseDAO.update(obj, database_session)

        return obj.node_uuid

    @staticmethod  # @BaseDAO.database_operation
    def del_biosoptionsavail(data, database_session):
        try:
            data = database_session.query(BiosConfig).filter(
                BiosOptionsAvail.avail_list_id == data.get('avail_list_id')).first()
            BaseDAO.delete(data, database_session)
        except:
            return '0'
        return '1'
