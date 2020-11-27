import logging
import logging.handlers

class LogHelper(object):

    def __init__(self, app):
        app.config['LOGGING_LEVEL'] = logging.DEBUG
        app.config['LOGGING_FORMAT'] = '%(asctime)s %(levelname)s: %(message)s in %(filename)s:%(lineno)d]'
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(app.config['LOGGING_LEVEL'])
        app.logger.addHandler(stream_handler)