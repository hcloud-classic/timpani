import logging
import json

from flask import request
from .base import EndpointAction, DataParser
from ..nameko.api import ApimanagerClient
from .schema import AppAddService, Appkeepalive, AppNodetype, SetDataDir

logger = logging.getLogger(__name__)

class InternalAPI:

    parser = DataParser()

    def __init__(self,app):
        self.app = app
        self.client = ApimanagerClient()
        self.client.setapp(app)
        app.add_url_rule("/v1/app/nodetype", 'nodetype',
                         view_func=EndpointAction(self.nodetype), methods=['POST'])
        app.add_url_rule("/v1/app/addservice", 'addservice',
                         view_func=EndpointAction(self.addservice), methods=['POST'])
        app.add_url_rule("/v1/app/keepalive", 'keepalive',
                         view_func=EndpointAction(self.keepalive), methods=['POST'])
        app.add_url_rule("/v1/app/getbiosconfig", 'getbiosconfig',
                         view_func=EndpointAction(self.getbiosconfig), methods=['POST'])
        app.add_url_rule("/v1/app/checkdir", 'setdatadir',
                         view_func=EndpointAction(self.setdatadir), methods=['POST'])

    @parser.response_data
    def nodetype(self):
        self.app.logger.info("Get NodeType")
        dic_data = self.parser.GetJson(AppNodetype(strict=True), request)
        dic_data['uuid'] = dic_data.get('node_uuid')
        self.app.logger.info("NodeType dic_data : {}".format(dic_data))
        res = self.client.send(method='getnodetype', msg=dic_data)
        return res
        # return info : nodetype, node config

    @parser.response_data
    def getbiosconfig(self):
        self.app.logger.info("Get getbiosconfig")
        dic_data = self.parser.GetJson(AppNodetype(strict=True), request)
        dic_data['uuid'] = dic_data.get('node_uuid')
        self.app.logger.info("getbiosconfig dic_data : {}".format(dic_data))
        res = self.client.send(method='getbiosconfig', msg=dic_data)
        return res

    @parser.response_data
    def addservice(self):
        self.app.logger.info("Get AddService")
        dic_data = self.parser.GetJson(AppAddService(strict=True), request)
        res = self.client.send(method='addservice', msg=dic_data)
        return res


    @parser.response_data
    def keepalive(self):
        self.app.logger.info("Get KeepAlive")
        dic_data = self.parser.GetJson(Appkeepalive(strict=True), request)
        res = self.client.send(method='keepalive', msg=dic_data)
        return res

    @parser.response_data
    def setdatadir(self):
        self.app.logger.info("setdatadir")
        json_str = request.get_data(as_text=True)
        self.app.logger.info("json_str : {}".format(json_str))
        dic_data = self.parser.GetJson(SetDataDir(strict=True), request)
        res = self.client.send(method='setdatadir', msg=dic_data)
        return res
