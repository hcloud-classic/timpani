import logging
import json

from flask import request
from .base import EndpointAction, DataParser
from timpani_gateway.nameko.api import ApimanagerClient
from .schema import IpmiConn, TemplateInit, TemplateList, CheckToken, SetTemplate, DumpBiosConfig, GetSyscfgDumpData

logger = logging.getLogger(__name__)

class BiosAPI:

    parser = DataParser()

    def __init__(self,app):
        self.app = app
        self.client = ApimanagerClient()
        self.client.setapp(app)
        app.add_url_rule("/v1/bios/init", 'templateinit',
                         view_func=EndpointAction(self.templateinit), methods=['POST'])
        app.add_url_rule("/v1/bios/gettemplate", 'gettemplatelist',
                         view_func=EndpointAction(self.gettemplatelist), methods=['POST'])
        app.add_url_rule("/v1/bios/biosconfiglist", 'biosconfiglist',
                         view_func=EndpointAction(self.biosconfiglist), methods=['POST'])
        app.add_url_rule("/v1/bios/settemplate", 'settemplate',
                         view_func=EndpointAction(self.settemplate), methods=['POST'])
        app.add_url_rule("/v1/bios/dumpbiosconfig", 'dumpbiosconfig',
                         view_func=EndpointAction(self.dumpbiosconfig), methods=['POST'])

        app.add_url_rule("/v1/bios/curtemplate", 'curtemplate',
                         view_func=EndpointAction(self.curtemplate), methods=['POST'])
        app.add_url_rule("/v1/bios/getsyscfgdumplist", 'getsyscfgdumplist',
                         view_func=EndpointAction(self.getsyscfgdumplist), methods=['POST'])
        app.add_url_rule("/v1/bios/getsyscfgdumpdata", 'getsyscfgdumpdata',
                         view_func=EndpointAction(self.getsyscfgdumpdata), methods=['POST'])

        app.add_url_rule("/v1/bios/getbioshist", 'getbioshist',
                         view_func=EndpointAction(self.bioshist), methods=['POST'])

    @parser.response_data
    def templateinit(self):
        self.app.logger.info("templateinit")
        # dic_data = self.parser.GetJson(TemplateInit(strict=True), request)
        # self.app.logger.info("templateinit ====> {}".format(dic_data))
        res = self.client.send(method='setbiostemplatedata', msg=None)

        return res

    @parser.response_data
    def gettemplatelist(self):
        self.app.logger.info("gettemplatelist")
        dic_data = self.parser.GetJson(TemplateList(strict=True), request)
        res = self.client.send(method='gettemplatelist', msg=dic_data)
        return res

    @parser.response_data
    def biosconfiglist(self):
        self.app.logger.info('biosconfig')
        dic_data = self.parser.GetJson(CheckToken(strict=True), request)
        res = self.client.biosconfiglist(dic_data)
        return res

    @parser.response_data
    def curtemplate(self):
        self.app.logger.info('curtemplate')
        dic_data = self.parser.GetJson(CheckToken(strict=True), request)
        res = self.client.curtemplate(dic_data)
        return res

    @parser.response_data
    def settemplate(self):
        self.app.logger.info("settemplate")
        dic_data = self.parser.GetJson(SetTemplate(strict=True), request)
        self.app.logger.info("settemplate ====> {}".format(dic_data))
        dic_data['runkind'] = 'set'
        res = self.client.setbiosconfig(dic_data)

        return res

    @parser.response_data
    def dumpbiosconfig(self):       # dump run command
        self.app.logger.info("dumpbiosconfig")
        dic_data = self.parser.GetJson(DumpBiosConfig(strict=True), request)
        self.app.logger.info("dumpbiosconfig ====> {}".format(dic_data))
        dic_data['runkind'] = 'dump'
        res = self.client.dumpbiosconfig(dic_data)

        return res

    @parser.response_data
    def getsyscfgdumplist(self):    # bios backup list
        self.app.logger.info("getsyscfgdumplist")
        dic_data = self.parser.GetJson(CheckToken(strict=True), request)
        self.app.logger.info("getsyscfgdumplist ====> {}".format(dic_data))
        # dic_data['getkind'] = 'dump'
        res = self.client.getsyscfgdumplist(dic_data)

        return res

    @parser.response_data
    def getsyscfgdumpdata(self):
        self.app.logger.info("getsyscfgdumpdata")
        dic_data = self.parser.GetJson(GetSyscfgDumpData(strict=True), request)
        self.app.logger.info("getsyscfgdumpdata ====> {}".format(dic_data))
        res = self.client.send(method='getsyscfgdumpdata_api',msg=dic_data)

        return res

    @parser.response_data
    def bioshist(self):
        self.app.logger.info("bioshist")
        dic_data = self.parser.GetJson(CheckToken(strict=True), request)
        dic_data['kind'] = "bios"
        res = self.client.GetProcessHist(dic_data)
        return res