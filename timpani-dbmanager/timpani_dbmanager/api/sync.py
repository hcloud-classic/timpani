import logging
import datetime
from timpani_dbmanager.db import dao
from .base import Base
from ..db.models.sync import SyncTableStatus
from timpani_dbmanager.db.dao.base_dao import BaseDAO
from timpani_base.constants import (SYNC_PROC_PRE, SYNC_PROC_UPDATE, SYNC_PROC_AFTER, SYNC_PROC_PARAM_NAME, SYNC_PROC_HIST,
                                    SYNC_TYPECODE_NODE, SYNC_KINDCODE_NODE, SYNC_DEFAULT_DELAY, SYNC_CODE_NODE, SYNC_NAME_NODE)

logger = logging.getLogger(__name__)

class SyncAPI(object):
    base = Base()

    SYNC_INIT_DATA = {
                    "sync_type_code": SYNC_TYPECODE_NODE,
                    "sync_kind_code": SYNC_KINDCODE_NODE,
                    "sync_code": SYNC_CODE_NODE,
                    "sync_delay": int(SYNC_DEFAULT_DELAY),
                    "sync_name": SYNC_NAME_NODE,
                    "sync_last_result": 0,
                    "sync_last_runtime": None
                }

    def syncnodelist(self, nodelist, database_session):
        sync_node_list = dao.node_dao.SyncNodeDAO.getobjlist_syncnode(database_session=database_session)
        islistdel = True

        if sync_node_list is None:
            islistdel = False

        for nodeinfo in nodelist:
            logger.info("data : {}".format(nodeinfo))
            uuid = nodeinfo.get('uuid').replace('-', '').upper()
            server_uuid = nodeinfo.get('server_uuid')
            sync_data_obj = dao.node_dao.SyncNodeDAO.getobj_nodeuuid(uuid, server_uuid,
                                                                     database_session=database_session)
            dao.node_dao.SyncNodeDAO.SyncNodeUpdate(sync_data_obj, nodeinfo, database_session=database_session)

            if islistdel:
                for old_obj in sync_node_list:
                    if old_obj.uuid.__eq__(nodeinfo.get('uuid')):
                        sync_node_list.remove(old_obj)
        if islistdel:
            if len(sync_node_list) > 0:
                for old_obj in sync_node_list:
                    dao.node_dao.SyncNodeDAO.SyncNodeDel(old_obj, database_session=database_session)

    def syncvolumelist(self, volumelist, database_session):
        sync_volume_list = dao.node_dao.SyncVolumeDAO.getobjlist_syncvolume(database_session=database_session)
        islistdel = True

        if sync_volume_list is None:
            islistdel = False

        for volumeinfo in volumelist:
            logger.info("data : {}".format(volumeinfo))
            uuid = volumeinfo.get('uuid').replace('-', '').upper()
            server_uuid = volumeinfo.get('server_uuid')
            user_uuid = volumeinfo.get('user_uuid')
            sync_data_obj = dao.node_dao.SyncVolumeDAO.getobj_volumeuuid(volumeinfo.get('uuid'), server_uuid, user_uuid,
                                                                     database_session=database_session)
            dao.node_dao.SyncVolumeDAO.SyncVolumeUpdate(sync_data_obj, volumeinfo, database_session=database_session)

            if islistdel:
                for old_obj in sync_volume_list:
                    if old_obj.uuid.__eq__(volumeinfo.get('uuid')):
                        sync_volume_list.remove(old_obj)
        if islistdel:
            if len(sync_volume_list) > 0:
                for old_obj in sync_volume_list:
                    dao.node_dao.SyncVolumeDAO.SyncVolumeDel(old_obj, database_session=database_session)

    @BaseDAO.database_operation
    def synccheck(self, data, database_session):
        logger.info("[SYNCCHECK] {}".format(data))
        res_code = '0000'
        sync_proc = data.get(SYNC_PROC_PARAM_NAME)

        logger.info("sync_proc : {}".format(sync_proc))
        if sync_proc.__eq__(SYNC_PROC_PRE):
            logger.info("ENTER SYNC PRE")
            sync_data_obj = dao.sync_dao.SyncStatusDAO.getobj_syncname(data.get('sync_name'), database_session=database_session)
            if sync_data_obj is None:
                # Init Data Insert
                dao.sync_dao.SyncStatusDAO.syncupdate(self.SYNC_INIT_DATA, sync_data_obj,
                                                      database_session=database_session)
                return {SYNC_PROC_PARAM_NAME : sync_proc, 'result': res_code, 'continue': True}
            else:
                now_date = datetime.datetime.now()
                if sync_data_obj.sync_last_runtime is None:
                    return {SYNC_PROC_PARAM_NAME: sync_proc, 'result': res_code, 'continue': True}
                delta = (now_date - sync_data_obj.sync_last_runtime).total_seconds()
                logger.info("now_date : {}".format(now_date))
                logger.info("sync_last_runtime : {}".format(sync_data_obj.sync_last_runtime))
                logger.info("delta : {}".format(delta))
                if delta > sync_data_obj.sync_delay:
                    logger.info("check time over True")
                    return {SYNC_PROC_PARAM_NAME: sync_proc, 'result': res_code, 'continue': True}
                else:
                    logger.info("check time over False")
                    return {SYNC_PROC_PARAM_NAME: sync_proc, 'result': res_code, 'continue': True}

        elif sync_proc.__eq__(SYNC_PROC_UPDATE):
            logger.info("ENTER SYNC UPDATE")
            nodelist = None
            volumelist = None
            nodedata = data.get('data')
            if nodedata is not None:
                nodelist = nodedata.get('nodelist')
                volumelist = nodedata.get('volumelist')

            if nodelist is None and volumelist is None:
                res_code = "6090"
                return {SYNC_PROC_PARAM_NAME: sync_proc, 'result': res_code, 'continue': False}

            if nodelist is not None:
                try:
                    self.syncnodelist(nodelist, database_session)
                except Exception as e:
                    logger.info("EXCEPTION : {}".format(e))
                    res_code = "6091"
                    return {SYNC_PROC_PARAM_NAME: sync_proc, 'result': res_code, 'continue': False}

            if volumelist is not None:
                try:
                    self.syncvolumelist(volumelist, database_session)
                except Exception as e:
                    logger.info("EXCEPTION : {}".format(e))
                    res_code = "6092"
                    return {SYNC_PROC_PARAM_NAME: sync_proc, 'result': res_code, 'continue': False}

            return {SYNC_PROC_PARAM_NAME: sync_proc, 'result': res_code, 'continue': True}

        elif sync_proc.__eq__(SYNC_PROC_AFTER):
            logger.info("ENTER SYNC AFTER : data {}".format(data))
            sync_data_obj = dao.sync_dao.SyncStatusDAO.getobj_syncname(data.get('sync_name'),
                                                                       database_session=database_session)
            sync_data = self.SYNC_INIT_DATA
            sync_data['sync_last_result'] = int(data.get('sync_result'))
            sync_data['sync_last_runtime'] = data.get('sync_start_at')
            dao.sync_dao.SyncStatusDAO.syncupdate(sync_data, sync_data_obj, database_session=database_session)
            return {SYNC_PROC_PARAM_NAME: sync_proc, 'result': res_code, 'continue': True}

        elif sync_proc.__eq__(SYNC_PROC_HIST):
            logger.info("ENTER SYNC HIST")
            dao.sync_dao.SyncHistDAO.synchistupdate(data, database_session=database_session)

        return {SYNC_PROC_PARAM_NAME: sync_proc, 'result': res_code}

    @BaseDAO.database_operation
    def getNodetype(self, data, database_session):
        res = dao.node_dao.SyncNodeDAO.getnodetype(data, database_session)
        return res

    @BaseDAO.database_operation
    def getnodelist(self, data, database_session):
        res = dao.node_dao.SyncNodeDAO.getnodelist(database_session)
        return res

    @BaseDAO.database_operation
    def getvolumelist(self, data, database_session):
        res = dao.node_dao.SyncVolumeDAO.getvolumelist(database_session)
        return res
