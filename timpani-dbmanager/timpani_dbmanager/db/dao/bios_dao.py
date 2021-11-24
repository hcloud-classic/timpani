import logging
from .base_dao import BaseDAO
from ..models.bios import (Bios, BiosConfig, BiosConfigHistory, BiosConfigList, BiosOptions,
                           BiosOptionsAvail, BiosOptionsAvailList,
                           BiosRedfishAvail, BiosRedfishMatch, BiosTemplate,
                           BiosCurBiosconfig, BiosCurTemplate, BiosBackup)
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

######################################### [template] #######################################################

class BiosRedfishAvailDAO(BaseDAO):
    FIELD = ["redfish_key", "cfg_set_val", "redfish_val"]

    @staticmethod
    def setdata(data, database_session):
        cfg_set_val = data.get('cfg_set_val')
        redfish_val = data.get('redfish_val')
        redfish_key = data.get('redfish_key')
        query = database_session.query(BiosRedfishAvail).filter(BiosRedfishAvail.redfish_key == redfish_key)
        query = query.filter(BiosRedfishAvail.redfish_val == redfish_val)
        query = query.filter(BiosRedfishAvail.cfg_set_val == cfg_set_val).first()
        field_list = BiosRedfishAvailDAO.FIELD
        if query is None:
            obj = BiosRedfishAvail()
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)

            return obj.id

        return query.id

    @staticmethod
    def getdata(data, database_session):
        if 'redfish_key' in data:
            redfish_key = data.get('redfish_key')
        else:
            redfish_key = None

        if 'redfish_val' in data:
            redfish_val = data.get('redfish_val')
        else:
            redfish_val = None

        query = database_session.query(BiosRedfishAvail.redfish_key,
                                       BiosRedfishAvail.cfg_set_val,
                                       BiosRedfishAvail.redfish_val)
        if redfish_key is not None:
            query = query.filter(BiosRedfishAvail.redfish_key == redfish_key)

        if redfish_val is not None:
            query = query.filter(BiosRedfishAvail.redfish_val == redfish_val)

        query = query.all()

        if query is None:
            return None
        else:
            res = BaseDAO.return_data(query=query, field_list=BiosRedfishAvailDAO.FIELD)

        return res

    @staticmethod
    def delAll(database_session):
        try:
            query = database_session.query(BiosRedfishAvail).all()
            for obj in query:
                BaseDAO.delete(obj, database_session)
            return '1'
        except Exception as e:
            return '0'


class BiosRedfishMatchDAO(BaseDAO):
    FIELD = ["match_kind", "syscfg_key", "redfish_key"]

    @staticmethod
    def setdata(data, database_session):
        syscfg_key = data.get('syscfg_key')
        match_kind = data.get('match_kind')
        redfish_key = data.get('redfish_key')
        query = database_session.query(BiosRedfishMatch).filter(BiosRedfishMatch.redfish_key == redfish_key)
        query = query.filter(BiosRedfishMatch.match_kind == match_kind)
        query = query.filter(BiosRedfishMatch.syscfg_key == syscfg_key).first()
        field_list = BiosRedfishMatchDAO.FIELD
        if query is None:
            obj = BiosRedfishMatch()
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)

            return obj.id

        return query.id

    @staticmethod
    def getdata(data, database_session):
        if 'redfish_key' in data:
            redfish_key = data.get('redfish_key')
        else:
            redfish_key = None

        if 'match_kind' in data:
            match_kind = data.get('match_kind')
        else:
            match_kind = None

        query = database_session.query(BiosRedfishMatch.match_kind,
                                       BiosRedfishMatch.syscfg_key,
                                       BiosRedfishMatch.redfish_key)
        if redfish_key is not None:
            query = query.filter(BiosRedfishMatch.redfish_key == redfish_key)

        if match_kind is not None:
            query = query.filter(BiosRedfishMatch.match_kind == match_kind)

        query = query.all()

        if query is None:
            return None
        else:
            res = BaseDAO.return_data(query=query, field_list=BiosRedfishMatchDAO.FIELD)

        return res

    @staticmethod
    def delAll(database_session):
        try:
            query = database_session.query(BiosRedfishMatch).all()
            for obj in query:
                BaseDAO.delete(obj, database_session)
            return '1'
        except Exception as e:
            return '0'


class BiosTemplateDAO(BaseDAO):
    FIELD = ["name", "redfish_key", "redfish_val", "cfg_set_val"]

    @staticmethod
    def setdata(data, database_session):
        name = data.get('name')
        cfg_set_val = data.get('cfg_set_val')
        redfish_val = data.get('redfish_val')
        redfish_key = data.get('redfish_key')
        query = database_session.query(BiosTemplate).filter(BiosTemplate.redfish_key == redfish_key)
        query = query.filter(BiosTemplate.redfish_val == redfish_val)
        query = query.filter(BiosTemplate.cfg_set_val == cfg_set_val)
        query = query.filter(BiosTemplate.name == name).first()
        field_list = BiosTemplateDAO.FIELD
        if query is None:
            obj = BiosTemplate()
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)

            return obj.id

        return query.id

    @staticmethod
    def getdata(data, database_session):
        if 'redfish_key' in data:
            redfish_key = data.get('redfish_key')
        else:
            redfish_key = None

        if 'redfish_val' in data:
            redfish_val = data.get('redfish_val')
        else:
            redfish_val = None

        if 'name' in data:
            name = data.get('name')
        else:
            name = None

        query = database_session.query(BiosTemplate.name,
                                   BiosTemplate.redfish_key,
                                   BiosTemplate.redfish_val,
                                   BiosTemplate.cfg_set_val)
        if redfish_key is not None:
            query = query.filter(BiosTemplate.redfish_key == redfish_key)

        if redfish_val is not None:
            query = query.filter(BiosTemplate.redfish_val == redfish_val)

        if name is not None:
            query = query.filter(BiosTemplate.name == name)

        query = query.all()

        if query is None:
            return None
        else:
            res = BaseDAO.return_data(query=query, field_list=BiosTemplateDAO.FIELD)

        return res

    @staticmethod
    def gettemplatelist(data, database_session):

        FIELD = ["name", "redfish_key", "syscfg_key", "cfg_set_val"]

        if 'match_kind' in data:
            match_kind = data.get('match_kind')
            if match_kind is None or match_kind.__eq__(''):
                match_kind = 'Default'
        else:
            match_kind = 'Default'

        query = database_session.query(BiosTemplate.name,
                                       BiosTemplate.redfish_key,
                                       BiosRedfishMatch.syscfg_key,
                                       BiosTemplate.cfg_set_val)
        query = query.join(BiosRedfishMatch, BiosRedfishMatch.match_kind == match_kind)
        query = query.filter(BiosRedfishMatch.redfish_key == BiosTemplate.redfish_key).all()

        if query is None:
            return None
        else:
            template_data_list = BaseDAO.return_data(query=query, field_list=FIELD)

        res_data = []
        for templatedata in template_data_list:
            name = templatedata.get('name')

            issave = True
            for priv_template in res_data:
                if priv_template.get('name').__eq__(name):
                    priv_template.get('data').append(templatedata)
                    issave = False

            if issave:
                save_data = {'name': name, 'data': [templatedata]}
                res_data.append(save_data)

        return res_data

    @staticmethod
    def delAll(database_session):
        try:
            query = database_session.query(BiosTemplate).all()
            for obj in query:
                BaseDAO.delete(obj, database_session)
            return '1'
        except Exception as e:
            return '0'

class BiosCurBiosconfigDAO(BaseDAO):

    FIELD = ['sub_id', 'macaddr', 'guid', 'section', 'syscfg_key', 'cfg_set_val']

    @staticmethod
    def setdata(data, database_session):
        obj = BiosCurBiosconfig()
        BaseDAO.set_value(obj,BiosCurBiosconfigDAO.FIELD, data)
        BaseDAO.insert(obj, database_session)

        return obj.sub_id

    @staticmethod
    def getsubid(data, database_session):
        query = database_session.query(BiosCurBiosconfig)
        query = query.filter(BiosCurBiosconfig.macaddr == data.get('macaddr'))
        query = query.order_by(BiosCurBiosconfig.sub_id.desc()).first()

        if query is None:
            return None

        return query.sub_id

    @staticmethod
    def getdata(data, database_session):
        query = database_session.query(BiosCurBiosconfig.section,
                                       BiosCurBiosconfig.syscfg_key,
                                       BiosCurBiosconfig.cfg_set_val)
        query = query.filter(BiosCurBiosconfig.macaddr == data.get('macaddr'))
        query = query.filter(BiosCurBiosconfig.sub_id == data.get('sub_id')).all()
        if query is None:
            return []

        FIELD = ["section","key","value"]
        res = BaseDAO.return_data(query=query, field_list=FIELD)
        return res

    @staticmethod
    def deldata(sub_id, database_session):
        query = database_session.query(BiosCurBiosconfig).filter(BiosCurBiosconfig.sub_id==sub_id).all()
        if query is None:
            return False

        for obj in query:
            BaseDAO.delete(obj, database_session)
        return True

class BiosCurTemplateDAO(BaseDAO):

    FIELD = ['macaddr', 'guid', 'name', 'redfish_key', 'syscfg_key',
             'match_kind', 'cfg_set_val', 'redfish_val', 'cfg_bios_ver', 'cfg_fw_opcode']

    @staticmethod
    def setdata(data, database_session):
        obj = BiosCurTemplate()
        BaseDAO.set_value(obj, BiosCurTemplateDAO.FIELD, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def getdata(data, database_session):
        query = database_session.query(BiosCurTemplate.name,
                                       BiosCurTemplate.match_kind,
                                       BiosCurTemplate.redfish_key,
                                       BiosCurTemplate.syscfg_key,
                                       BiosCurTemplate.cfg_set_val,
                                       BiosCurTemplate.redfish_val,
                                       BiosCurTemplate.cfg_bios_ver,
                                       BiosCurTemplate.cfg_fw_opcode)
        query = query.filter(BiosCurTemplate.macaddr == data.get('macaddr')).all()
        if query is None:
            return []

        FIELD = ["name", "match_kind", "redfish_key","syscfg_key","cfg_set_val","redfish_val",
                 "cfg_bios_ver","cfg_fw_opcode"]
        res = BaseDAO.return_data(query=query, field_list=FIELD)
        return res

    @staticmethod
    def deldata(macaddr, database_session):
        query = database_session.query(BiosCurTemplate).filter(BiosCurTemplate.macaddr == macaddr).all()
        if query is None:
            return False

        for obj in query:
            BaseDAO.delete(obj, database_session)
        return True

class BiosBackupDAO(BaseDAO):
    FIELD = ['macaddr', 'guid', 'kind', 'backupname', 'sys_bios_ver', 'sys_me_ver',
             'sys_sdr_ver', 'sys_bmc_ver', 'template_name', 'syscfg_path', 'syscfg_filename',
             'redfish_filename', 'syscfg_sub_id']

    @staticmethod
    def setdata(data, database_session):
        obj = BiosBackup()
        BaseDAO.set_value(obj, BiosBackupDAO.FIELD, data)
        BaseDAO.insert(obj, database_session)

        return obj.id

    @staticmethod
    def getdata(data, database_session):
        FIELD = ['macaddr', 'guid', 'kind', 'backupname', 'sys_bios_ver', 'sys_me_ver',
                 'sys_sdr_ver', 'sys_bmc_ver', 'template_name', 'syscfg_path', 'syscfg_filename',
                 'redfish_filename', 'syscfg_sub_id', 'time']
        query = database_session.query(BiosBackup.macaddr,
                                       BiosBackup.guid,
                                       BiosBackup.kind,
                                       BiosBackup.backupname,
                                       BiosBackup.sys_bios_ver,
                                       BiosBackup.sys_me_ver,
                                       BiosBackup.sys_sdr_ver,
                                       BiosBackup.sys_bmc_ver,
                                       BiosBackup.template_name,
                                       BiosBackup.syscfg_path,
                                       BiosBackup.syscfg_filename,
                                       BiosBackup.redfish_filename,
                                       BiosBackup.syscfg_sub_id,
                                       BiosBackup.register_dt)
        query = query.filter(BiosBackup.macaddr == data.get('macaddr'))
        if 'getkind' in data:
            if data.get('getkind') is not None:
                query = query.filter(BiosBackup.kind == data.get('getkind'))
        query = query.order_by(BiosBackup.register_dt.desc()).all()

        if query is None:
            return []

        res = BaseDAO.return_data(query=query, field_list=FIELD)
        return res

    @staticmethod
    def getbiosconfig(data, database_session):
        FIELD = ['macaddr', 'guid', 'kind', 'backupname', 'sys_bios_ver', 'sys_me_ver',
                 'sys_sdr_ver', 'sys_bmc_ver', 'template_name', 'syscfg_path', 'syscfg_filename',
                 'redfish_filename', 'syscfg_sub_id', 'time']
        query = database_session.query(BiosBackup.macaddr,
                                       BiosBackup.guid,
                                       BiosBackup.kind,
                                       BiosBackup.backupname,
                                       BiosBackup.sys_bios_ver,
                                       BiosBackup.sys_me_ver,
                                       BiosBackup.sys_sdr_ver,
                                       BiosBackup.sys_bmc_ver,
                                       BiosBackup.template_name,
                                       BiosBackup.syscfg_path,
                                       BiosBackup.syscfg_filename,
                                       BiosBackup.redfish_filename,
                                       BiosBackup.syscfg_sub_id,
                                       BiosBackup.register_dt)
        query = query.filter(BiosBackup.macaddr == data.get('macaddr'))
        if 'getkind' in data:
            query = query.filter(BiosBackup.kind == data.get('getkind'))
        query = query.order_by(BiosBackup.register_dt.desc()).first()

        if query is None:
            return None

        res = BaseDAO.return_data(query=query, field_list=BiosBackupDAO.FIELD)
        return res

    @staticmethod
    def deldata(backupname, database_session):
        query = database_session.query(BiosBackup).filter(BiosBackup.backupname == backupname).first()
        if query is None:
            return False

        BaseDAO.delete(query, database_session)
        return True



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
