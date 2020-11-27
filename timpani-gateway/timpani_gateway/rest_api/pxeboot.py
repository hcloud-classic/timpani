import logging
import json

from flask import request
from .base import EndpointAction, DataParser
from timpani_gateway.nameko.api import ApimanagerClient
from .schema import IpmiConn

logger = logging.getLogger(__name__)

class PxebootAPI:

    parser = DataParser()

    def __init__(self,app):
        self.app = app
        self.client = ApimanagerClient()
        app.add_url_rule("/v1/pxeboot/registerPXEBootImage", 'registerImage', view_func=EndpointAction(self.registerImage), methods=['POST'])
        app.add_url_rule("/v1/pxeboot/uploadPXEBootImageFile", 'uploadImageFile', view_func=EndpointAction(self.uploadImageFile),
                         methods=['POST'])
        app.add_url_rule("/v1/pxeboot/deletePXEBootImageFile", 'deletePXEBootImageFile',
                         view_func=EndpointAction(self.deletePXEBootImageFile),
                         methods=['POST'])
        app.add_url_rule("/v1/pxeboot/getPXEBootImage", 'getPXEBootImage', view_func=EndpointAction(self.getPXEBootImage),
                         methods=['POST'])
        app.add_url_rule("/v1/pxeboot/updatePXEBootImage", 'updatePXEBootImage',
                         view_func=EndpointAction(self.updatePXEBootImage),
                         methods=['POST'])
        app.add_url_rule("/v1/pxeboot/deletePXEBootImage", 'deletePXEBootImage', view_func=EndpointAction(self.deletePXEBootImage),
                         methods=['POST'])
        app.add_url_rule("/v1/pxeboot/registerPXEBootConfig", 'registerPXEBootConfig', view_func=EndpointAction(self.registerPXEBootConfig),
                         methods=['POST'])
        app.add_url_rule("/v1/pxeboot/getPXEBootConfig", 'getPXEBootConfig',
                         view_func=EndpointAction(self.getPXEBootConfig),
                         methods=['POST'])
        app.add_url_rule("/v1/pxeboot/updatePXEBootConfig", 'updatePXEBootConfig',
                         view_func=EndpointAction(self.updatePXEBootConfig),
                         methods=['POST'])
        app.add_url_rule("/v1/pxeboot/deletePXEBootConfig", 'deletePXEBootConfig',
                         view_func=EndpointAction(self.deletePXEBootConfig),
                         methods=['POST'])
        app.add_url_rule("/v1/pxeboot/history/getPXEBootHistory", 'getPXEBootHistory',
                         view_func=EndpointAction(self.getPXEBootHistory),
                         methods=['POST'])
        app.add_url_rule("/v1/pxeboot/history/deletePXEBootHistory", 'deletePXEBootHistory',
                         view_func=EndpointAction(self.deletePXEBootHistory),
                         methods=['POST'])


    # Register Node
    @parser.response_data
    def registerImage(self):
        self.app.logger.info("registerImage")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        res = self.client.send(method='registerIPMIConn',msg = dic_data)

        return json.dumps(res)

    @parser.response_data
    def uploadImageFile(self, nodeuuid):
        self.app.logger.info("registerIPMIConn")
        dic_data = self.parser.GetJson(IpmiConn(strict=True), request)
        dic_data['conn_id'] = nodeuuid
        res = self.client.send(method='updateIPMIConn', msg=dic_data)

        return json.dumps(res)

    @parser.response_data
    def deleteImageFile(self, nodeuuid):
        self.app.logger.info("registerIPMIConn")
        dic_data = {'conn_id':nodeuuid}
        res = self.client.send(method='deleteIPMIConn', msg=dic_data)

        return json.dumps(res)