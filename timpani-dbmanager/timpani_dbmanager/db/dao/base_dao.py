import logging
from timpani_dbmanager.db.db_connect_handler import DBConnectHandler
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

class BaseDAO:

    @staticmethod
    def database_operation(func):
        def wrapped_function(*params, **kwargs):
            handler = DBConnectHandler()
            _, req_param = params
            kwargs['database_session'] = handler.session
            if 'page_msg' in req_param.keys():
                page_msg = req_param.get('page_msg')
            else:
                page_msg = ''

            while True:
                try:
                    responses = func(*params, **kwargs)
                    # handler.session.commit()
                    #handler.session.rollback()
                    # handler.session.close()
                    return responses
                except OperationalError:
                    handler.session.rollback()
                    # handler.session.close()
                    errorcode = "E0406"
                    errorstr = "Exception OperationlError"
                    responses = {'errorcode': errorcode, 'errorstr': errorstr, 'page_msg': page_msg}
                    logger.info("Exception OperationlError")
                    return responses
                except Exception as e:
                    handler.session.rollback()
                    # handler.session.close()
                    logger.info("Exception raised {}".format(e))
                    # logger.info("Exception DB kwargs {}".format(params))
                    errorcode = "6001"
                    errorstr = "DB Internal Error"
                    responses = {'errorcode': errorcode, 'errorstr': errorstr, 'page_msg': page_msg}
                    return responses

        return wrapped_function

    @staticmethod
    def set_value(obj, field_list, data):
        for field in field_list:
            if hasattr(obj, field):
                if isinstance(data.get(field), type(None)):
                    setattr(obj, field, None)
                else:
                    setattr(obj, field, data.get(field))
        return obj

    @staticmethod
    def update_value(obj, field_list, data):
        for field in field_list:
            if hasattr(obj, field):
                if not isinstance(data.get(field), type(None)):
                    setattr(obj, field, data.get(field))

    @staticmethod
    def insert(obj, database_session):
        database_session.add(obj)
        database_session.flush()
        database_session.refresh(obj)

    @staticmethod
    def update(obj, database_session):
        # database_session.add(obj
        database_session.flush()
        # database_session.refresh(obj)

    @staticmethod
    def delete(obj, database_session):
        database_session.delete(obj)
        database_session.flush()





