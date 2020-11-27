import logging
import json

from flask import request
from .base import EndpointAction, DataParser
from timpani_gateway.nameko.api import ApimanagerClient
from .schema import IpmiConn

logger = logging.getLogger(__name__)

class IpmiNode:

    parser = DataParser()

    def __init__(self,app):
        self.app = app
        self.client = ApimanagerClient()
        app.add_url_rule("/v1/ipmi/registerNode", 'registerIPMIConn', view_func=EndpointAction(self.registerIPMIConn), methods=['POST'])
        app.add_url_rule("/v1/ipmi/getNode", 'getIPMIConn', view_func=EndpointAction(self.registerIPMIConn),
                         methods=['POST'])
        app.add_url_rule("/v1/ipmi/updateNode", 'updateIPMIConn', view_func=EndpointAction(self.updateIPMIConn),
                         methods=['POST'])
        app.add_url_rule("/v1/ipmi/deleteNode", 'deleteIPMIConn', view_func=EndpointAction(self.deleteIPMIConn),
                         methods=['POST'])


    # Register Node
    @parser.response_data
    def registerIPMIConn(self):
        self.app.logger.info("registerIPMIConn")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        res = self.client.send(method='registerIPMIConn',msg = dic_data)

        return json.dumps(res)

    # show ipmi connection information
    @parser.response_data
    def getIPMIConn(self, nodeuuid):
        self.app.logger.info("registerIPMIConn")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        dic_data['conn_id'] = nodeuuid
        res = self.client.send(method='updateIPMIConn', msg=dic_data)

        return json.dumps(res)

    # change ipmi connection value
    @parser.response_data
    def updateIPMIConn(self, nodeuuid):
        self.app.logger.info("registerIPMIConn")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        dic_data['conn_id'] = nodeuuid
        res = self.client.send(method='updateIPMIConn', msg=dic_data)

        return json.dumps(res)

    # delete ipmi connection Information
    @parser.response_data
    def deleteIPMIConn(self, nodeuuid):
        self.app.logger.info("registerIPMIConn")
        dic_data = {'conn_id':nodeuuid}
        res = self.client.send(method='deleteIPMIConn', msg=dic_data)

        return json.dumps(res)