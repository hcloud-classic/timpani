import logging
import json
import bcrypt

from flask import request
from .base import EndpointAction, DataParser
from timpani_gateway.nameko.api import ApimanagerClient
from .schema import Login, CheckToken, MasterSync
from ..gql_client.GqlClient import GqlClient
from ..jwt.jwt import jwtutil
from timpani_base.constants import QL_URL

logger = logging.getLogger(__name__)

class AuthAPI:

    parser = DataParser()
    JWT_SECRET = 'secret'
    JWT_ALGORITHM = 'HS256'
    JWT_EXP_DELTA_SECONDS = 60

    def __init__(self,app):
        self.app = app
        self.client = ApimanagerClient()
        self.client.setapp(app)
        self.gqlclient = GqlClient(QL_URL, app)
        app.add_url_rule("/v1/login", 'login',
                         view_func=EndpointAction(self.login), methods=['POST'])
        app.add_url_rule("/v1/locallogin", 'locallogin',
                         view_func=EndpointAction(self.locallogin), methods=['POST'])
        app.add_url_rule("/v1/checktoken", 'checktoken',
                         view_func=EndpointAction(self.checktoken), methods=['POST'])

        app.add_url_rule("/v1/mastersync", 'mastersync',
                         view_func=EndpointAction(self.mastersync), methods=['POST'])

    @parser.response_data
    def login(self):
        # argment : user_id, password (SHA-256 -> bCrypto)
        self.app.logger.info("Login")
        dic_data = self.parser.GetJson(Login(), request)
        self.app.logger.info("login dic_data : {}".format(dic_data))
        res = self.client.login(dic_data.get('user'), dic_data.get('password'))
        self.app.logger.info("login res_data : {}".format(res))
        return res

    @parser.response_data
    def locallogin(self):
        self.app.logger.info("LocalLogin")
        jwt = jwtutil()
        dic_data = self.parser.GetJson(Login(), request)
        try:
            res = self.client.PasswordCheck(dic_data.get('user'), dic_data.get('password'))
        except Exception as e:
            res = False
        self.app.logger.info("LocalLogin passwordcheck : {}".format(res))

        if res:
            token = jwt.createToken().decode('utf-8')
        else:
            token = None
        self.app.logger.info("LocalLogin token : {}".format(token))
        return {'token': token}


    @parser.response_data
    def checktoken(self):
        self.app.logger.info("checktoken")
        dic_data = self.parser.GetJson(CheckToken(), request)
        self.app.logger.info(dic_data.get('internal'))
        isvalid, userid, groupid, authentication, isinternal = self.client.CheckToken(dic_data.get('token'))
        res = {'isvalid': isvalid,
               'user_id': userid,
               'group_id': groupid,
               'authentication': authentication}

        return res

    @parser.response_data
    def mastersync(self):
        dic_data = self.parser.GetJson(MasterSync(), request)
        res = self.client.mastersync(dic_data.get('username'), dic_data.get('password'))
        self.app.logger.info("res : {}".format(res))
        return res

