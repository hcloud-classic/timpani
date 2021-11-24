import uuid
import logging

from datetime import datetime

from .base_dao import BaseDAO
from ..models.app import App, TimpaniConfig, ModuleStatus, DataDir

from sqlalchemy.sql import compiler
from sqlalchemy.dialects import mysql
logger = logging.getLogger(__name__)

class AppDAO(BaseDAO):

    APP_FIELD = ['uuid', 'nodetype', 'ipaddress', 'macaddress']
    APP_INFO_FIELD = ["uuid", "nodetype", "ipaddress", "macaddress", "register_dt"]

    @staticmethod
    def appupdate(data, database_session):
        field_list = AppDAO.APP_FIELD
        obj = database_session.query(App).filter(App.uuid == data.get('uuid')).first()
        if obj is None:
            obj = App()
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)
        else:
            BaseDAO.update_value(obj, field_list, data)
            BaseDAO.update(obj, database_session)

        return obj.id

    @staticmethod
    def getappinfo(data, database_session):
        if 'node_uuid' in data:
            uuid = data.get('node_uuid').replace('-', '').upper()
            data['uuid'] = uuid
        elif 'uuid' in data:
            uuid = data.get('uuid')
        query = database_session.query(App.uuid, App.nodetype, App.ipaddress, App.macaddress, App.register_dt)
        query = query.filter(App.uuid == uuid).first()
        res = BaseDAO.return_data(query=query, field_list=AppDAO.APP_INFO_FILED)

        return res

    @staticmethod
    def getappinfoobj(data, database_session):
        if 'node_uuid' in data:
            uuid = data.get('node_uuid').replace('-', '').upper()
            data['uuid'] = uuid
        elif 'uuid' in data:
            uuid = data.get('uuid')
        query = database_session.query(App)
        obj = query.filter(App.uuid == uuid).first()

        return obj

    @staticmethod
    def delapp(data, database_session):
        try:
            if 'node_uuid' in data:
                uuid = data.get('node_uuid').replace('-', '').upper()
                data['uuid'] = uuid
            elif 'uuid' in data:
                uuid = data.get('uuid')
            query = database_session.query(App)
            query = query.filter(App.uuid == uuid).first()
            if query is None:
                return '0'
            BaseDAO.delete(query, database_session)
        except:
            return '0'
        return '1'


class ModuleStatusDAO(BaseDAO):
    APP_FIELD = ['pid', 'modulename', 'moduletype', 'start_at', 'check_at', 'appinfo_id']

    @staticmethod
    def modulestatusupdate(data, database_session):
        field_list = ModuleStatusDAO.APP_FIELD
        query = database_session.query(ModuleStatus).filter(ModuleStatus.moduletype == data.get('moduletype'))
        obj = query.filter(ModuleStatus.pid == data.get('pid')).first()
        if obj is None:
            obj = ModuleStatus()
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)
        else:
            BaseDAO.update_value(obj, field_list, data)
            BaseDAO.update(obj, database_session)

        return obj.id

    @staticmethod
    def getmodulestatus(data, database_session):
        query = database_session.query(ModuleStatus.pid, ModuleStatus.modulename,
                                       ModuleStatus.moduletype, ModuleStatus.start_at,
                                       ModuleStatus.check_at, ModuleStatus.appinfo_id)
        query = query.filter(ModuleStatus.pid == data.get('pid'))
        query = query.filter(ModuleStatus.moduletype == data.get('moduletype')).first()
        res = BaseDAO.return_data(query=query, field_list=ModuleStatusDAO.APP_FIELD)

        return res

    @staticmethod
    def getmodulename(data, database_session):
        INFO_FIELD = ['modulename', 'uuid']
        query = database_session.query(ModuleStatus.modulename, App.uuid)
        query = query.join(App, App.id == ModuleStatus.appinfo_id)
        if 'nodetype' in data:
            query = query.filter(App.nodetype == data.get('nodetype'))
        query = query.filter(ModuleStatus.moduletype == data.get('moduletype'))
        query = query.filter(ModuleStatus.check_at.between(data.get('priv_dt'), data.get('now_dt')))
        logger.info(BaseDAO.debug_sql_print(query, 'getmodulename'))
        query = query.all()
        res = BaseDAO.return_data(query=query, field_list=INFO_FIELD)
        logger.info("getmodulename res : {}".format(res))
        return res

    @staticmethod
    def delmodulestatus(data, database_session):
        try:
            query = database_session.query(ModuleStatus)
            query = query.filter(ModuleStatus.pid == data.get('pid')).first()
            if query is None:
                return '0'
            BaseDAO.delete(query, database_session)
        except:
            return '0'
        return '1'


class TimpaniConfigDAO(BaseDAO):
    FIELD = ['rabbit_id', 'rabbit_pass', 'rabbit_port', 'backup_ip', 'backup_nic', 'master_nic',
            'storage_nic', 'ipmimanager_nic', 'master_data_prefix', 'storage_data_prefix',
            'nfs_export_path', 'nfs_mount_path', 'osbackup_api_ip', 'osbackup_api_port']

    @staticmethod
    def setConfig(data, database_session):
        field_list = TimpaniConfigDAO.FIELD
        obj = database_session.query(TimpaniConfig).first()
        if obj is None:
            obj = TimpaniConfig()
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)
        else:
            BaseDAO.update_value(obj, field_list, data)
            BaseDAO.update(obj, database_session)

        return obj.id

    @staticmethod
    def getConfig(data, database_session):

        if 'get_kind' in data:
            getkind = data.get('get_kind')
        else:
            getkind = 'ALL'

        if getkind.__eq__('MASTER'):
            field_list = ['rabbit_id', 'rabbit_pass', 'rabbit_port', 'master_nic', 'master_data_prefix']
            query = database_session.query(TimpaniConfig.rabbit_id,
                                           TimpaniConfig.rabbit_pass,
                                           TimpaniConfig.rabbit_port,
                                           TimpaniConfig.master_nic,
                                           TimpaniConfig.master_data_prefix
                                           )
        elif getkind.__eq__('STORAGE'):
            field_list = ['rabbit_id','rabbit_pass','rabbit_port','storage_nic','storage_data_prefix']
            query = database_session.query(TimpaniConfig.rabbit_id,
                                           TimpaniConfig.rabbit_pass,
                                           TimpaniConfig.rabbit_port,
                                           TimpaniConfig.storage_nic,
                                           TimpaniConfig.storage_data_prefix,
                                           )
        elif getkind.__eq__('IPMI'):
            field_list = ['rabbit_id', 'rabbit_pass', 'rabbit_port', 'ipmimanager_nic']
            query = database_session.query(TimpaniConfig.rabbit_id,
                                           TimpaniConfig.rabbit_pass,
                                           TimpaniConfig.rabbit_port,
                                           TimpaniConfig.ipmimanager_nic
                                           )
        elif getkind.__eq__('NFS'):
            field_list = ['backup_ip', 'nfs_export_path', 'nfs_mount_path', 'osbackup_api_ip', 'osbackup_api_port']
            query = database_session.query(TimpaniConfig.backup_ip,
                                           TimpaniConfig.nfs_export_path,
                                           TimpaniConfig.nfs_mount_path,
                                           TimpaniConfig.osbackup_api_ip,
                                           TimpaniConfig.osbackup_api_port
                                           )
        else:
            field_list = TimpaniConfigDAO.FIELD
            query = database_session.query(TimpaniConfig.rabbit_id,
                                           TimpaniConfig.rabbit_pass,
                                           TimpaniConfig.rabbit_port,
                                           TimpaniConfig.backup_ip,
                                           TimpaniConfig.backup_nic,
                                           TimpaniConfig.master_nic,
                                           TimpaniConfig.storage_nic,
                                           TimpaniConfig.ipmimanager_nic,
                                           TimpaniConfig.master_data_prefix,
                                           TimpaniConfig.storage_data_prefix,
                                           TimpaniConfig.nfs_export_path,
                                           TimpaniConfig.nfs_mount_path,
                                           TimpaniConfig.osbackup_api_ip,
                                           TimpaniConfig.osbackup_api_port
                                           )
        query = query.first()
        res = BaseDAO.return_data(query=query, field_list=field_list)

        if getkind.__eq__('MASTER') or getkind.__eq__('STORAGE') or getkind.__eq__('IPMI'):
            if 'master_nic' in res:
                res['nicname'] = res.get('master_nic')
                res['prefix'] = res.get('master_data_prefix')
                del res['master_nic']
                del res['master_data_prefix']
            elif 'storage_nic' in res:
                res['nicname'] = res.get('storage_nic')
                res['prefix'] = res.get('storage_data_prefix')
                del res['storage_nic']
                del res['storage_data_prefix']
            elif 'ipmimanager_nic' in res:
                res['nicname'] = res.get('ipmimanager_nic')
                del res['ipmimanager_nic']

        return res

class DataDirDAO(BaseDAO):

    FIELD = ["uuid", 'usetype', "nodetype", "name", "modulename"]

    @staticmethod
    def setdata(data, database_session):
        obj = DataDir()
        BaseDAO.set_value(obj, DataDirDAO.FIELD, data)
        BaseDAO.insert(obj, database_session)

        return obj.uuid

    @staticmethod
    def getdata(data, database_session):
        FIELD = ["uuid", 'usetype', "nodetype", "name"]
        query = database_session.query(DataDir.uuid, DataDir.usetype, DataDir.nodetype, DataDir.name)
        query = query.filter(DataDir.uuid == data.get('uuid')).all()

        if query is None:
            return None

        res = BaseDAO.return_data(query=query, field_list=FIELD)

        return res



    @staticmethod
    def deldata(data, database_session):
        objlist = database_session.query(DataDir).filter(DataDir.uuid == data.get('uuid')).all()
        for obj in objlist:
            BaseDAO.delete(obj,database_session)
        return True
