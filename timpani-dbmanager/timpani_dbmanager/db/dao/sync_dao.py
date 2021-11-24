import logging
import datetime
from .base_dao import BaseDAO
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from ..models.sync import (SyncTableStatus, SyncTableHist
                             )
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

class SyncStatusDAO(BaseDAO):
    FIELD = ["sync_type_code", "sync_kind_code", "sync_code", "sync_name", "sync_delay",
             "sync_last_result", "sync_last_runtime"]
    FIND_KEY = "sync_name"
    INFO_FILED = ["sync_code", "sync_delay", "sync_last_runtime", "sync_last_result"]

    @staticmethod
    def syncupdate(data, obj, database_session):
        logger.info("SyncStatus UPDATE data : {}".format(data))
        field_list = SyncStatusDAO.FIELD
        # obj = SyncStatusDAO.search_equl_data(data.get(SyncStatusDAO.FIND_KEY), database_session)
        if obj is None:
            obj = SyncTableStatus()
            BaseDAO.set_value(obj, field_list, data)
            logger.info("sync_last_result : {}".format(obj.sync_last_result))
            logger.info("sync_last_runtime : {}".format(obj.sync_last_runtime))
            obj.sync_last_runtime = None
            BaseDAO.insert(obj, database_session)
        else:
            BaseDAO.update_value(obj, field_list, data)
            logger.info("sync_last_result : {}".format(obj.sync_last_result))
            logger.info("sync_last_runtime : {}".format(obj.sync_last_runtime))
            obj.sync_last_runtime = func.now()
            BaseDAO.update(obj, database_session)

        return obj.id

    @staticmethod
    def getobj_syncname(sync_name, database_session):
        obj = database_session.query(SyncTableStatus).filter(SyncTableStatus.sync_name == sync_name).first()
        if obj is None:
            return None
        return obj

    @staticmethod
    def getSyncStatus(data, database_session):
        query = database_session.query(SyncTableStatus.sync_code, SyncTableStatus.sync_delay,
                                       SyncTableStatus.sync_last_runtime, SyncTableStatus.sync_last_result)
        if data.get(SyncStatusDAO.FIND_KEY) is None:  # Find ALL Data
            query = query.all()
        else:  # Find User
            query = query.filter(SyncTableStatus.sync_name == data.get(SyncStatusDAO.FIND_KEY)).first()
        res = BaseDAO.return_data(query=query, field_list=SyncStatusDAO.INFO_FILED)

        return res

    @staticmethod
    def syncdatadel(obj, database_session):
        BaseDAO.delete(obj, database_session)
        return True


class SyncHistDAO(BaseDAO):
    FIELD = ["sync_type", "sync_code", "sync_name", "sync_start_at", "sync_stop_at", "sync_result",
             "sync_err_code", "sync_err_msg"]
    FIND_KEY = "sync_hist_id"
    INFO_FILED = ["sync_name", "sync_code", "sync_err_code", "sync_err_msg", "sync_start_at", "sync_stop_at", "sync_result",
             "register_dt"]

    @staticmethod
    def synchistupdate(data, database_session):
        field_list = SyncHistDAO.FIELD
        obj = None
        if "sync_hist_id" in data:
            obj = SyncHistDAO.getobj_synchist(data.get(SyncHistDAO.FIND_KEY), database_session)

        if obj is None:
            BaseDAO.set_value(obj, field_list, data)
            BaseDAO.insert(obj, database_session)
        else:
            BaseDAO.update_value(obj, field_list, data)
            BaseDAO.update(obj, database_session)

        return obj.id

    @staticmethod
    def getobj_synchist(id_val, database_session):
        obj = database_session.query(SyncTableHist).filter(SyncTableHist.id == id_val).first()
        if obj is None:
            return None
        return obj

    @staticmethod
    def getSyncHist(database_session):
        query = database_session.query(SyncTableHist.sync_name, SyncTableHist.sync_code,
                                       SyncTableHist.sync_err_code, SyncTableHist.sync_err_msg,
                                       SyncTableHist.sync_start_at, SyncTableHist.sync_stop_at,
                                       SyncTableHist.sync_result, SyncTableHist.register_dt)
        query = query.all()
        res = BaseDAO.return_data(query=query, field_list=SyncHistDAO.INFO_FILED)

        return res

