import logging
import json
import datetime
from pytz import timezone

from flask import request
from .base import EndpointAction, DataParser
from ..gql_client.GqlClient import GqlClient
from timpani_gateway.nameko.api import ApimanagerClient
from timpani_base.constants import (SYNC_PROC, SYNC_PROC_HIST, SYNC_PROC_PARAM_NAME, SYNC_PROC_UPDATE,
                                    SYNC_PROC_PRE, SYNC_PROC_AFTER)
from .schema import SyncCheck

logger = logging.getLogger(__name__)

class SyncAPI:
    parser = DataParser()
    app = None

    def __init__(self, app):
        self.app = app
        self.client = ApimanagerClient()
        self.client.setapp(app)  # DEBUG
        # self.gqlclient = GqlClient("http://192.168.221.1:38080/graphql", self.app)
        app.add_url_rule("/v1/synccheck", 'synccheck',
                         view_func=EndpointAction(self.synccheck), methods=['POST'])

    @parser.response_data
    def synccheck(self):
        self.app.logger.info("SyncCheck")
        dic_data = self.parser.GetJson(SyncCheck(strict=True), request)
        self.app.logger.info("Request Data : {}".format(dic_data))
        sync_proc_list = SYNC_PROC
        sync_name = dic_data['sync_name']
        res = self.client.synccheck(sync_name)
        # check_result = True
        # is_error = False
        # start_at = datetime.datetime.now(tz=timezone('Asia/Seoul'))
        # # start_at = datetime.datetime.now(tz=timezone('UTC'))
        #
        # try:
        #     for sync_proc in SYNC_PROC:
        #         check_data = {SYNC_PROC_PARAM_NAME: sync_proc, 'sync_name': sync_name}
        #         if sync_proc.__eq__(SYNC_PROC_PRE):
        #             self.app.logger.info("sync_proc:{}".format(SYNC_PROC_PRE))
        #         elif sync_proc.__eq__(SYNC_PROC_UPDATE):
        #             self.app.logger.info("sync_proc:{}".format(SYNC_PROC_UPDATE))
        #             nodelist, volumelist, token = self.NodeSyncRequest()
        #             # self.app.logger.info("token : {}".format(token))
        #             # self.app.logger.info("nodelist : {}".format(nodelist))
        #             # self.app.logger.info("volumelist : {}".format(volumelist))
        #             check_data['data'] = {'nodelist': nodelist, 'volumelist': volumelist}
        #         elif sync_proc.__eq__(SYNC_PROC_AFTER):
        #             self.app.logger.info("sync_proc:{}".format(SYNC_PROC_AFTER))
        #             check_data['sync_result'] = '1'
        #             check_data['sync_start_at'] = start_at
        #
        #         iscontinue, iserr, res = self.InternalSend(check_data, sync_proc)
        #         if iserr:
        #             break
        #
        #         if not iscontinue:
        #             self.app.logger.info('[{}] iscontinue False'.format(sync_proc))
        #             break
        #         self.app.logger.info('[{}] iscontinue True'.format(sync_proc))
        #
        # except Exception as e:
        #     self.app.logger.info("EXCEPTION : {}".format(e))
        #     check_result = False

        # self.app.logger.info("Respose Data : {}".format(check_result))
        return res

    def InternalSend(self, data, sync_proc):
        self.app.logger.info("data : {} \nsync_proc:{}".format(data, sync_proc))
        is_err = False
        res = None
        try:
            res = self.client.send(method='synccheck', msg=data)
        except Exception as e:
            is_err = True
            self.app.logger.info("sync_proc:{} [INTERNAL ERROR]".format(SYNC_PROC_AFTER))
        self.app.logger.info("SyncCheck Response Data : {}".format(res))

        if 'result' in res:
            if not res.get('result').__eq__('0000'):
                is_err = True
            else:
                self.app.logger.info('[{}] SUCCESS'.format(sync_proc))
        else:
            self.app.logger.info('ERROR')
            is_err = True

        iscontinue = res.get('continue')
        return iscontinue, is_err, res

    # Sync Node Data Request
    def NodeSyncRequest(self):
        # Get Token
        username = "root"
        password = "$2a$10$6c4oT2kB9XiG6eueFtSyc.DY2cFiy7rSFn/Do4Qb1cl4NhN6i0Hgm"
        token = None
        nodelistresp = None
        volumelistresp = None
        nodelist = None
        volumelist = None

        token = self.client.GetToken(username, password)

        # Get Data
        if token is not None:
            # self.app.logger.info("GET NODE LIST")
            # self.app.logger.info("GET VOLUME LIST")
            nodelist = self.client.GetNodeList(token)
            volumelist = self.client.GetVolumeList(token)
        return nodelist, volumelist, token


    def SyncHist(self, sync_name, errcode, msg, result, start_at):
        end_at = datetime.datetime.now(tz=True)
        sync_hist_data = {
            'sync_proc': SYNC_PROC_HIST,
            'sync_name': sync_name,
            'sync_err_code': errcode,
            'sync_result': result,
            'sync_err_msg': msg,
            'sync_start_at':start_at,
            'sync_end_at':end_at
        }

        try:
            res = self.client.send(method='synccheck', msg=sync_hist_data)
        except Exception as e:
            is_error = True
            self.app.logger.info("sync_proc:{} [INTERNAL ERROR]".format(SYNC_PROC_AFTER))

        pass
