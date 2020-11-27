import logging
import json

from flask import request
from .base import EndpointAction, DataParser
from timpani_gateway.nameko.api import ApimanagerClient
from .schema import IpmiConn

logger = logging.getLogger(__name__)

class FirmwareAPI:

    parser = DataParser()

    def __init__(self,app):
        self.app = app
        self.client = ApimanagerClient()
        app.add_url_rule("/v1/firmware/registerFirmwareDepandency", 'registerfirmwaredepandency',
                         view_func=EndpointAction(self.registerfirmwaredepandency), methods=['POST'])
        app.add_url_rule("/v1/firmware/uploadFirmwareFile", 'firmwarefileupload',
                         view_func=EndpointAction(self.firmwarefileupload), methods=['POST'])
        app.add_url_rule("/v1/firmware/registerFirmware", 'registerfirmware',
                         view_func=EndpointAction(self.registerfirmware), methods=['POST'])
        app.add_url_rule("/v1/firmware/updateFirmware", 'updatefirmware',
                         view_func=EndpointAction(self.updatefirmware), methods=['POST'])
        app.add_url_rule("/v1/firmware/getAvailFirmwareList", 'getavailfirmwarelist',
                         view_func=EndpointAction(self.getavailfirmwarelist), methods=['POST'])      # availiable registed firmware file list
        app.add_url_rule("/v1/firmware/getFirmwareList", 'getfirmwarelist',
                         view_func=EndpointAction(self.getfirmwarelist), methods=['POST'])           # registed firmware file list
        app.add_url_rule("/v1/firmware/deleteFirmwareFile", 'deletefirmwarefile',
                         view_func=EndpointAction(self.deletefirmwarefile), methods=['POST'])
        app.add_url_rule("/v1/firmware/deleteFirmware", 'deletefirmware',
                         view_func=EndpointAction(self.deletefirmware), methods=['POST'])
        app.add_url_rule("/v1/firmware/deleteFirmwareDepandency", 'deletefirmwaredepandency',
                         view_func=EndpointAction(self.deletefirmwaredepandency), methods=['POST'])
        app.add_url_rule("/v1/firmware/history/getFirmwareHistory", 'getfirmwarehistory',
                         view_func=EndpointAction(self.getfirmwarehistory), methods=['POST'])
        app.add_url_rule("/v1/firmware/history/deleteFirmwareHistory", 'deletefirmwarehistory',
                         view_func=EndpointAction(self.deletefirmwarehistory), methods=['POST'])


    # Register Node
    @parser.response_data
    def registerfirmwaredepandency(self):
        self.app.logger.info("registerfirmwaredepandency")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        res = self.client.send(method='registerfirmwaredepandency',msg = dic_data)

        return json.dumps(res)

    @parser.response_data
    def firmwarefileupload(self):
        self.app.logger.info("firmwarefileupload")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        dic_data = None
        res = self.client.send(method='firmwarefileupload', msg=dic_data)

        return json.dumps(res)

    @parser.response_data
    def registerfirmware(self):
        self.app.logger.info("registerfirmware")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        dic_data = None
        res = self.client.send(method='registerfirmware', msg=dic_data)

        return json.dumps(res)

    @parser.response_data
    def updatefirmware(self, nodeuuid):
        self.app.logger.info("updatefirmware")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        dic_data = {'node_uuid': nodeuuid}
        res = self.client.send(method='updatefirmware', msg=dic_data)

        return json.dumps(res)

    @parser.response_data
    def getavailfirmwarelist(self, nodeuuid):
        self.app.logger.info("getavailfirmwarelist")
        dic_data = {'node_uuid': nodeuuid}
        res = self.client.send(method='getavailfirmwarelist', msg=dic_data)

        return json.dumps(res)

    @parser.response_data
    def getfirmwarelist(self):
        self.app.logger.info("getfirmwarelist")
        dic_data = None
        res = self.client.send(method='getfirmwarelist', msg=dic_data)

        return json.dumps(res)

    @parser.response_data
    def deletefirmware(self, firmwareid):
        self.app.logger.info("deletefirmware")
        dic_data = {'id': firmwareid}
        res = self.client.send(method='deletefirmware', msg=dic_data)

        return json.dumps(res)

    @parser.response_data
    def deletefirmwarefile(self, firmwareid):
        self.app.logger.info("deletefirmwarefile")
        dic_data = {'id': firmwareid}
        res = self.client.send(method='deletefirmwarefile', msg=dic_data)

        return json.dumps(res)

    @parser.response_data
    def deletefirmwaredepandency(self, depandencyid):
        self.app.logger.info("deletefirmwaredepandency")
        dic_data = {'id': depandencyid}
        res = self.client.send(method='deletefirmwaredepandency', msg=dic_data)

        return json.dumps(res)

    @parser.response_data
    def getfirmwarehistory(self):
        self.app.logger.info("getfirmwarehistory")
        dic_data = None
        res = self.client.send(method='getfirmwarehistory', msg=dic_data)

        return json.dumps(res)

    @parser.response_data
    def registerfirmware(self, histid):
        self.app.logger.info("deletefirmwarehistory")
        dic_data = {'id': histid}
        res = self.client.send(method='deletefirmwarehistory', msg=dic_data)

        return json.dumps(res)