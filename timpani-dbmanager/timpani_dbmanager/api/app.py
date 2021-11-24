import logging
import datetime
from pytz import timezone
from timpani_dbmanager.db import dao
from .base import Base
from ..db.dao.base_dao import BaseDAO

import uuid

logger = logging.getLogger(__name__)

class AppAPI(object):
    base = Base()

    @BaseDAO.database_operation
    def setconfig(self, data, database_session):
        logger.info('[setconfig] data : {}'.format(data))
        # data['id_name'] = data.get('username')
        res_data = dao.app_dao.TimpaniConfigDAO.setConfig(data, database_session=database_session)
        return res_data

    @BaseDAO.database_operation
    def getconfig(self, data, database_session):
        logger.info('[getconfig] data : {}'.format(data))
        # data['id_name'] = data.get('username')
        res_data = dao.app_dao.TimpaniConfigDAO.getConfig(data, database_session=database_session)
        return res_data

    @BaseDAO.database_operation
    def addservice(self, data, database_session):
        logger.info('[addservice] data : {}'.format(data))
        now_date = datetime.datetime.now(tz=timezone('Asia/Seoul'))
        uuid = data.get('node_uuid').replace('-', '').upper()
        data['uuid'] = uuid
        appinfo = {'uuid': uuid, 'nodetype': data.get('nodetype'),
                   'ipaddress': data.get('ipaddress'), 'macaddress': data.get('macaddress')}
        appinfo_id = dao.app_dao.AppDAO.appupdate(appinfo, database_session)
        modulename = "{}{}{}".format(data.get('nodetype'), data.get('moduletype'), appinfo_id)
        modulestatus = {
            'pid':data.get('pid'), 'modulename':modulename, 'moduletype': data.get('moduletype'),
            'start_at': now_date, 'check_at': now_date, 'appinfo_id': appinfo_id
        }
        modulestatus_id = dao.app_dao.ModuleStatusDAO.modulestatusupdate(modulestatus, database_session)
        resdata = {'modulename': modulename}
        return resdata

    @BaseDAO.database_operation
    def keepalive(self, data, database_session):
        logger.info('[keepalive] data : {}'.format(data))
        getmodulestatus = dao.app_dao.ModuleStatusDAO.getmodulestatus(data, database_session)
        if 'pid' in getmodulestatus:
            now_date = datetime.datetime.now(tz=timezone('Asia/Seoul'))
            getmodulestatus['check_at'] = now_date
            modulestatus_id = dao.app_dao.ModuleStatusDAO.modulestatusupdate(getmodulestatus, database_session)

            return {'result': True}
        return {'result': False}

    @BaseDAO.database_operation
    def getmodulename(self, data, database_session):
        logger.info('[getmodulename] data : {}'.format(data))
        now_date = datetime.datetime.now(tz=timezone('Asia/Seoul'))
        data['priv_dt'] = now_date - datetime.timedelta(seconds=30)
        data['now_dt'] = now_date
        res = dao.app_dao.ModuleStatusDAO.getmodulename(data, database_session)

        return res

    @BaseDAO.database_operation
    def setdatadir(self, data, database_session):

        postdata = data.get('postdata')
        uuid = postdata[0].get('uuid')
        del_data = {'uuid':uuid}
        dao.app_dao.DataDirDAO.deldata(del_data, database_session)

        for datadirdata in postdata:
            dao.app_dao.DataDirDAO.setdata(datadirdata, database_session)

        return {'isvalid': True}

    @BaseDAO.database_operation
    def getdatadir(self, data, database_session):
        res = dao.app_dao.DataDirDAO.getdata(data, database_session)
        return res
