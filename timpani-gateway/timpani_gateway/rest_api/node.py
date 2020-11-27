import logging
import json
from flask import request
from .base import EndpointAction, DataParser
from timpani_gateway.nameko.api import ApimanagerClient
from .schema import RegisterNode, UpdateNode, RegisterNode_V1

logger = logging.getLogger(__name__)

class RestNode:

    parser = DataParser()

    def __init__(self,app):
        self.app = app
        self.client = ApimanagerClient()
        app.add_url_rule("/v1/node/registerNode", 'RegisterNode', view_func=EndpointAction(self.RegisterNode), methods=['POST'])
        app.add_url_rule("/v1/node/getAllList", 'getNodeList', view_func=EndpointAction(self.getNodeList), methods=['POST'])
        app.add_url_rule("/v1/node/getLeaderList", 'getNodeLeader', view_func=EndpointAction(self.getNodeLeaderList), methods=['POST'])
        app.add_url_rule("/v1/node/getComputeList", 'getNodeComputeList', view_func=EndpointAction(self.getNodeComputeList), methods=['POST'])
        app.add_url_rule("/v1/node/getNodeInfo", 'getNodeInfo', view_func=EndpointAction(self.getNodeInfo) , methods=['POST'])
        app.add_url_rule("/v1/node/updateNode", 'updateNode', view_func=EndpointAction(self.updateNode), methods=['POST'])
        app.add_url_rule("/v1/node/deleteNode", 'deleteNode', view_func=EndpointAction(self.deleteNode), methods=['POST'])


    # Register Node
    @parser.response_data
    def RegisterNode(self):
        self.app.logger.info("RegisterNode")
        dic_data = self.parser.GetJson(RegisterNode_V1(strict=True), request)
        self.app.logger.info("Request Data : {}".format(dic_data))
        res = self.client.send(method='registerNode',msg = dic_data)
        self.app.logger.info("Respose Data : {}".format(res))
        return res

    # All Node List
    @parser.response_data
    def getNodeList(self):
        self.app.logger.info("getNodeList")
        dic_data = {'nodeuuid': None, 'search_kind': 0}
        res = self.client.send(method='getNodeList', msg=dic_data)
        return res

    # Leader Node List
    @parser.response_data
    def getNodeLeaderList(self):
        self.app.logger.info("getNodeLeaderList")
        dic_data = {'nodeuuid': None, 'search_kind': 1}
        res = self.client.send(method='getNodeLeaderList', msg=dic_data)
        return res

    # Compute Node List
    @parser.response_data
    def getNodeComputeList(self):
        self.app.logger.info("getNodeComputeList nodeuuid : {}".format(nodeuuid))
        dic_data = {'nodeuuid': nodeuuid, 'search_kind': 2}
        res = self.client.send(method='getNodeComputeList', msg=dic_data)
        return res

    # Get Node Info
    @parser.response_data
    def getNodeInfo(self):
        self.app.logger.info("getNodeInfo nodeuuid : {}".format(nodeuuid))
        dic_data = {'nodeuuid': nodeuuid, 'search_kind':3}
        res = self.client.send(method='getNodeInfo', msg=dic_data)
        return res

    # Updete Node
    @parser.response_data
    def updateNode(self):
        self.app.logger.info("updateNode: nodeuuid : {}".format(nodeuuid))
        dic_data = self.parser.GetJson(UpdateNode(strict=True), request)
        dic_data['nodeuuid'] = nodeuuid
        res = self.client.send(method='updateNode', msg=dic_data)
        return res

    # Delete Node Info
    @parser.response_data
    def deleteNode(self):
        self.app.logger.info("deleteNode nodeuuid : {}".format(nodeuuid))
        dic_data = {'nodeuuid':nodeuuid}
        res = self.client.send(method='deleteNode', msg=dic_data)
        return res

