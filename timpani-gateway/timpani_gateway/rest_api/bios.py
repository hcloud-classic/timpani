import logging
import json

from flask import request
from .base import EndpointAction, DataParser
from timpani_gateway.nameko.api import ApimanagerClient
from .schema import IpmiConn

logger = logging.getLogger(__name__)

class BiosAPI:

    parser = DataParser()

    def __init__(self,app):
        self.app = app
        self.client = ApimanagerClient()
        app.add_url_rule("/v1/bios/getBiosConfig", 'getbiosconfig',
                         view_func=EndpointAction(self.getbiosconfig), methods=['POST'])
        app.add_url_rule("/v1/bios/updateBiosConfig", 'updatebiosconfig',
                         view_func=EndpointAction(self.updatebiosconfig), methods=['POST'])
        app.add_url_rule("/v1/bios/refresh", 'refreshbiosconfig',
                         view_func=EndpointAction(self.refreshbiosconfig), methods=['POST'])             # Control API
        app.add_url_rule("/v1/bios/history/getHistory", 'historybiosconfig',
                         view_func=EndpointAction(self.historybiosconfig), methods=['POST'])
        app.add_url_rule("/v1/bios/history/getHistoryBiosConfig", 'gethistorybiosconfig',
                         view_func=EndpointAction(self.gethistorybiosconfig), methods=['POST'])
        app.add_url_rule("/v1/bios/history/updateHistoryBiosConfig", 'updatehistorybiosconfig',
                         view_func=EndpointAction(self.updatehistorybiosconfig), methods=['POST'])
        app.add_url_rule("/v1/bios/history/deleteHistoryBiosConfig", 'deletehistorybiosconfig',
                         view_func=EndpointAction(self.deletehistorybiosconfig), methods=['POST'])


    # Bios Config Information
    @parser.response_data
    def getbiosconfig(self, nodeuuid):
        self.app.logger.info("getbiosconfig")
        dic_data = None
        dic_data['node_uuid'] = nodeuuid
        res = self.client.send(method='getbiosconfig',msg= dic_data)

        return json.dumps(res)

    # Bios Update
    @parser.response_data
    def updatebiosconfig(self, nodeuuid):
        self.app.logger.info("updatebiosconfig")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        dic_data['node_uuid'] = nodeuuid
        res = self.client.send(method='updatebiosconfig', msg=dic_data)

        return json.dumps(res)

    #Bios config Refrash
    @parser.response_data
    def refreshbiosconfig(self, nodeuuid):
        self.app.logger.info("refreshbiosconfig")
        dic_data = None
        res = self.client.send(method='refreshbiosconfig', msg=dic_data)

        return json.dumps(res)

    # Bios Update
    @parser.response_data
    def historybiosconfig(self, nodeuuid):
        self.app.logger.info("historybiosconfig")
        dic_data = None
        dic_data['node_uuid'] = nodeuuid
        res = self.client.send(method='historybiosconfig', msg=dic_data)

        return json.dumps(res)

    # Bios Update
    @parser.response_data
    def gethistorybiosconfig(self, nodeuuid, configid):
        self.app.logger.info("gethistorybiosconfig")
        dic_data = None
        dic_data['node_uuid'] = nodeuuid
        dic_data['config_id'] = configid
        res = self.client.send(method='gethistorybiosconfig', msg=dic_data)

        return json.dumps(res)

    # Bios Update
    @parser.response_data
    def updatehistorybiosconfig(self, nodeuuid, configid):
        self.app.logger.info("updatehistorybiosconfig")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        dic_data['node_uuid'] = nodeuuid
        dic_data['config_id'] = configid

        res = self.client.send(method='updatehistorybiosconfig', msg=dic_data)

        return json.dumps(res)

    # Bios Update
    @parser.response_data
    def deletehistorybiosconfig(self, nodeuuid, configid):
        self.app.logger.info("deletehistorybiosconfig")
        dic_data = None
        dic_data['node_uuid'] = nodeuuid
        dic_data['config_id'] = configid
        res = self.client.send(method='deletehistorybiosconfig', msg=dic_data)

        return json.dumps(res)