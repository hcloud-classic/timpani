import logging
import json

from flask import request
from .base import EndpointAction, DataParser
from timpani_gateway.nameko.api import ApimanagerClient
from .schema import GetRecoverList, SetSystemHistory, SystemBackup, SystemRecover, GetBackupSrcList, SystemHistory, Backup

logger = logging.getLogger(__name__)

class SystemAPI:

    parser = DataParser()

    def __init__(self,app):
        self.app = app
        self.client = ApimanagerClient()
        app.add_url_rule("/v1/filesystem/getBackupSrcList", 'getbackupsrclist',
                         view_func=EndpointAction(self.getbackupsrclist), methods=['POST'])
        app.add_url_rule("/v1/filesystem/getRecoverList", 'getrecoverlist',
                         view_func=EndpointAction(self.getrecoverlist), methods=['POST'])
        app.add_url_rule("/v1/filesystem/backup", 'bakup',
                         view_func=EndpointAction(self.backup), methods=['POST'])
        app.add_url_rule("/v1/filesystem/recover", 'systemrecover',
                         view_func=EndpointAction(self.systemrecover), methods=['POST'])
        app.add_url_rule("/v1/filesystem/history/getSystemHistory", 'getsystemhistory',
                         view_func=EndpointAction(self.getsystemhistorybackup), methods=['POST'])
        app.add_url_rule("/v1/filesystem/history/getHistoryBackup", 'getsystemhistorybakup',
                         view_func=EndpointAction(self.getsystemhistorybackup), methods=['POST'])
        app.add_url_rule("/v1/filesystem/history/getHistoryRecover", 'getsystemhistoryrecover',
                         view_func=EndpointAction(self.getsystemhistoryrecover), methods=['POST'])
        app.add_url_rule("/v1/filesystem/history/getHistoryError", 'getsystemhistoryerror',
                         view_func=EndpointAction(self.getsystemhistoryerror), methods=['POST'])
        app.add_url_rule("/v1/filesystem/history/deleteHistory", 'deletesystemhistory',
                         view_func=EndpointAction(self.deletesystemhistory), methods=['POST'])
        app.add_url_rule("/v1/filesystem/history/setHistory", 'setsystemhistory',
                         view_func=EndpointAction(self.setsystemhistory), methods=['POST'])

    # Backup Target Source List
    @parser.response_data
    def getbackupsrclist(self):
        self.app.logger.info("getbackupsrclist")
        dic_data = self.parser.GetJson(GetBackupSrcList(strict=True), request)
        self.app.logger.info("getbackupsrclist : send before")
        res = self.client.send(method='getbackupsrclist', msg=dic_data)
        return res

    @parser.response_data
    def getrecoverlist(self):
        self.app.logger.info("getrecoverlist")
        dic_data = self.parser.GetJson(GetRecoverList(strict=True), request)
        self.app.logger.info("getrecoverlist : send before")
        res = self.client.send(method='getrecoverlist', msg=dic_data)
        return res

    @parser.response_data
    def systembackup(self):
        self.app.logger.info("systembackup")
        dic_data = self.parser.GetJson(SystemBackup(strict=True), request)
        dic_data['backup_kind'] = 'increment'
        res = self.client.send(method='systembackup', msg= dic_data)

        return res

    @parser.response_data
    def backup(self):
        self.app.logger.info("backup command")
        dic_data = self.parser.GetJson(Backup(strict=True), request)
        res = self.client.send(method='backupcmd', msg=dic_data)

        return res

    @parser.response_data
    def systemrecover(self):
        self.app.logger.info("systemrecover")
        dic_data = self.parser.GetJson(SystemRecover(strict=True), request)
        res = self.client.send(method='systemrecover', msg= dic_data)
        return res

    @parser.response_data
    def getsystemhistory(self):
        self.app.logger.info("getsystemhistory")
        dic_data = self.parser.GetJson(SystemHistory(strict=True), request)
        res = None
        if 'target_type_list' in dic_data:
            res = self.client.send(method='getsystemhistory', msg=dic_data)
        else:
            dic_data['target_type_list'] = ['backup', 'recover', 'error']
            res = self.client.send(method='getsystemhistory', msg=dic_data)

        return res

    @parser.response_data
    def getsystemprocesshistory(self):
        self.app.logger.info("getsystemprocesshistory")
        dic_data = self.parser.GetJson(SystemHistory(strict=True), request)
        res = None
        if 'target_type_list' in dic_data:
            res = self.client.send(method='getsystemprocesshistory', msg=dic_data)
        else:
            dic_data['target_type_list'] = ['backup', 'recover', 'error']
            res = self.client.send(method='getsystemprocesshistory', msg=dic_data)

        return res

    @parser.response_data
    def getsystemhistorybackup(self):
        self.app.logger.info("getsystemhistorybackup")
        dic_data = self.parser.GetJson(SystemHistory(strict=True), request)
        dic_data['target_type_list'] = ['backup']
        res = self.client.send(method='getsystemprocesshistory', msg=dic_data)
        return res

    @parser.response_data
    def getsystemhistoryrecover(self):
        self.app.logger.info("getsystemhistoryrecover")
        dic_data = self.parser.GetJson(SystemHistory(strict=True), request)
        dic_data['target_type_list'] = ['recover']
        # dic_data['node_uuid'] = nodeuuid
        res = self.client.send(method='getsystemprocesshistory',msg= dic_data)

        return res

    @parser.response_data
    def getsystemhistoryerror(self):
        self.app.logger.info("getsystemhistoryerror")
        dic_data = self.parser.GetJson(SystemHistory(strict=True), request)
        dic_data['target_type_list'] = ['error']
        # dic_data['node_uuid'] = nodeuuid
        res = self.client.send(method='getsystemprocesshistory', msg=dic_data)

        return res

    @parser.response_data
    def deletesystemhistory(self):
        self.app.logger.info("deletesystemhistory")
        dic_data = None
        # dic_data['node_uuid'] = nodeuuid
        # dic_data['id'] = histid
        res = self.client.send(method='deletesystemhistory',msg= dic_data)

        return json.dumps(res)

    @parser.response_data
    def setsystemhistory(self):
        self.app.logger.info("setsystemhistory")
        dic_data = None
        dic_data = self.parser.GetJson(SetSystemHistory(strict=True), request)
        res = self.client.send(method='setsystemhistory', msg= dic_data)

        return json.dumps(res)
