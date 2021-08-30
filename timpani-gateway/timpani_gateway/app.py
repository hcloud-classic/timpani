import click
import yaml
import json
from flask import Flask, jsonify, Response

from .config import Config
from .schema import Schema
from .rest_api.node import RestNode
from .rest_api.ipmi import IpmiNode
from .rest_api.system import SystemAPI
from .rest_api.sync import SyncAPI
from .rest_api.log_helper import LogHelper
from .rest_api.auth import AuthAPI

from .exceptions import InvalidError, InvalidException

import logging.handlers
################################### logger ############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d][%(levelname)-8s] %(message)s : (%(filename)s:%(lineno)s)', datefmt="%Y-%m-%d %H:%M:%S")
fileHandler = logging.handlers.TimedRotatingFileHandler(filename='./log_'+__name__.__str__(), when='midnight', backupCount=0, interval=1, encoding='utf-8')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
stream_hander = logging.StreamHandler()
logger.addHandler(stream_hander)
#######################################################################################################################

def create_app(*config_cls):
    app = Flask(__name__)

    @app.errorhandler(InvalidError)
    def handle_invalid_usage(error):
        return jsonify(error.to_dict()), 400

    @app.errorhandler(InvalidException)
    def handle_invalid_exception(error):
        return jsonify(error.to_dict()), 500

    for config in config_cls:
        app.config.from_object(config)
    logger.info("START APPLICATION")
    LogHelper(app)
    Schema(app)
    IpmiNode(app)

    '''
    Restful API Setting
    '''
    RestNode(app)
    SystemAPI(app)
    AuthAPI(app)
    SyncAPI(app)

    return app


def start_app(url, port):
    app = create_app(Config)
    app.run(**Config.RUN_SETTING)


@click.option('--address', is_flag=False, help="Setting Flask Server IPV4 Address")
@click.option('--port', is_flag=False, help="Setting Flask Server Port")
@click.option('--config', type=click.Path(exists=False), help="Configuration yaml file Path")
@click.command()
def main(address, port, config):
    """
    Config Value Setting
    """
    cfg = None
    if config:
        with open(config) as f:
            cfg = yaml.unsafe_load(f)

    if address:
        address = address

    if port:
        port = port

    start_app(address, port)


if __name__ == '__main__':
    main()
