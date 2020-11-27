import logging
import json

from flask import request
from .base import EndpointAction, DataParser
from timpani_gateway.nameko.api import ApimanagerClient
from .schema import IpmiConn

logger = logging.getLogger(__name__)

class SystemAPI:

    parser = DataParser()

    def __init__(self,app):
        self.app = app
        self.client = ApimanagerClient()
        app.add_url_rule("/v1/filesystem/getZfsList", 'getzpoollist',
                         view_func=EndpointAction(self.getzpoollist), methods=['POST'])
        app.add_url_rule("/v1/filesystem/backup", 'systembakup',
                         view_func=EndpointAction(self.systembackup), methods=['POST'])
        app.add_url_rule("/v1/filesystem/recover", 'systemrecover',
                         view_func=EndpointAction(self.systemrecover), methods=['POST'])
        app.add_url_rule("/v1/filesystem/history/getHistoryBackup", 'getsystemhistorybakup',
                         view_func=EndpointAction(self.getsystemhistorybackup), methods=['POST'])
        app.add_url_rule("/v1/filesystem/history/getHistoryRecover", 'getsystemhistoryrecover',
                         view_func=EndpointAction(self.getsystemhistoryrecover), methods=['POST'])
        app.add_url_rule("/v1/filesystem/history/getHistoryError", 'getsystemhistoryerror',
                         view_func=EndpointAction(self.getsystemhistoryerror), methods=['POST'])
        app.add_url_rule("/v1/filesystem/history/deleteHistory", 'deletesystemhistory',
                         view_func=EndpointAction(self.deletesystemhistory), methods=['POST'])

    # Register Node
    @parser.response_data
    def getzpoollist(self, nodeuuid):
        self.app.logger.info("getzpoollist")
        dic_data = None
        dic_data['node_uuid'] = nodeuuid
        res = self.client.send(method='getzpoollist',msg= dic_data)

        return json.dumps(res)

    @parser.response_data
    def systembackup(self, nodeuuid):
        self.app.logger.info("systembackup")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        dic_data['node_uuid'] = nodeuuid
        res = self.client.send(method='systembackup',msg= dic_data)

        return json.dumps(res)

    @parser.response_data
    def systemrecover(self, nodeuuid):
        self.app.logger.info("systemrecover")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        dic_data['node_uuid'] = nodeuuid
        res = self.client.send(method='systemrecover',msg= dic_data)

        return json.dumps(res)

    @parser.response_data
    def getsystemhistorybackup(self, nodeuuid):
        self.app.logger.info("getsystemhistorybackup")
        dic_data = None
        dic_data['node_uuid'] = nodeuuid
        res = self.client.send(method='getsystemhistorybackup',msg= dic_data)

        return json.dumps(res)

    @parser.response_data
    def getsystemhistoryrecover(self, nodeuuid):
        self.app.logger.info("getsystemhistoryrecover")
        dic_data = None
        dic_data['node_uuid'] = nodeuuid
        res = self.client.send(method='getsystemhistoryrecover',msg= dic_data)

        return json.dumps(res)

    @parser.response_data
    def getsystemhistoryerror(self, nodeuuid):
        self.app.logger.info("getsystemhistoryerror")
        dic_data = None
        dic_data['node_uuid'] = nodeuuid
        res = self.client.send(method='getsystemhistoryerror',msg= dic_data)

        return json.dumps(res)

    @parser.response_data
    def deletesystemhistory(self, nodeuuid, histid):
        self.app.logger.info("deletesystemhistory")
        dic_data = None
        dic_data['node_uuid'] = nodeuuid
        dic_data['id'] = histid
        res = self.client.send(method='deletesystemhistory',msg= dic_data)

        return json.dumps(res)
