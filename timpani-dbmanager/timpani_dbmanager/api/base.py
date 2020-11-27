import logging

logger = logging.getLogger(__name__)

class Base(object):

    def error_catch(self, func):
        def catch(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
            except Exception as exc:
                logger.info(exc)
                errorcode = "E0402"
                errorstr = exc
                res = {'errorcode':errorcode, 'errorstr': errorstr}
            return res
        return catch

    def check_int(self, value):
        try:
            if isinstance(value,str):
                int(value)
                return True
            elif isinstance(value,int):
                return True
            else:
                logger.info("check_int : {}".format(type(value)))
                return False
        except ValueError:
            return False

