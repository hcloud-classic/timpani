import logging
from datetime import datetime
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
                    responses = {'errorcode': errorcode, 'errorstr': errorstr}
                    logger.info("Exception OperationlError")
                    return responses
                except Exception as e:
                    handler.session.rollback()
                    # handler.session.close()
                    logger.info("Exception raised {}".format(e))
                    # logger.info("Exception DB kwargs {}".format(params))
                    errorcode = "6001"
                    errorstr = "DB Internal Error"
                    responses = {'errorcode': errorcode, 'errorstr': errorstr}
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
        # logger.info("INSERT ENTER")
        database_session.add(obj)
        database_session.flush()
        database_session.refresh(obj)

    @staticmethod
    def update(obj, database_session):
        # logger.info("UPDATE ENTER")
        # database_session.add(obj
        database_session.flush()
        database_session.refresh(obj)

    @staticmethod
    def delete(obj, database_session):
        database_session.delete(obj)
        database_session.flush()

    @staticmethod
    def return_data(query, field_list, ins_field=None, ins_val=None):
        res = None

        if query is None:
            return res

        if isinstance(query, list):
            res = []
            for item in query:
                temp_list = list(item)
                cnt = 0
                temp_res = {}
                for field in field_list:
                    # logger.debug('type : {}'.format(type(temp_list[cnt])))
                    if isinstance(temp_list[cnt], datetime):
                        temp_list[cnt] = temp_list[cnt].strftime('%Y-%m-%d %H:%M:%S')
                    temp_res[field] = temp_list[cnt]
                    cnt += 1
                # logger.debug('temp_res : {}'.format(temp_res))
                if ins_field is not None:
                    temp_res[ins_field] = ins_val
                res.append(temp_res)
        else:
            temp_list = list(query)
            cnt = 0
            temp_res = {}
            for field in field_list:
                # logger.debug('type : {}'.format(type(temp_list[cnt])))
                if isinstance(temp_list[cnt], datetime):
                    temp_list[cnt] = temp_list[cnt].strftime('%Y-%m-%d %H:%M:%S')
                temp_res[field] = temp_list[cnt]
                cnt += 1
            # logger.debug('temp_res : {}'.format(temp_res))
            res = temp_res

        return res

    @staticmethod
    def debug_sql_print(query, func_name):
        logger.info("SQL [ {} ] : {}".format(func_name, query.statement.compile(compile_kwargs={"literal_binds": True})))





