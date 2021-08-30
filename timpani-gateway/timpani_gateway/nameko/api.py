import nameko
import bcrypt
from nameko.standalone.rpc import ClusterRpcClient
from timpani_gateway.constants import AMQP_CONFIG
from ..rest_api.base import DataParser

class ApimanagerClient():

    restbase = DataParser()

    def setapp(self, app):
        self.restbase.setapp(app)

    @nameko.config.patch(AMQP_CONFIG)
    def send(self, method, msg):
        print(AMQP_CONFIG['AMQP_URI'])
        with ClusterRpcClient() as rpc:
            call_method = getattr(rpc.apimanager_service, method)
            # res = call_method.call_async(msg)
            res = call_method(msg)
        return res

    def mastersync(self, username, password):
        # Login Test
        token = self.GetToken(username, password)
        if token is not None:
            msg = {'username': username, 'password': password}
            res = self.send("mastersync", msg)
            return res

        return None

    def logincheck(self, username, password):
        token = self.GetToken(username, password)
        if token is None:
            return "USER ACCOUNT MISSMATCHING"

        isvalid, userid, groupid, authentication = self.CheckToken(token)
        if authentication is not None:
            if authentication.upper().__eq__("MASTER"):
                msg = {'username': username, 'password': password}
                res = self.send("mastersync", msg)
            else:
                return "USER AUTHENTICATION MISSMATCHING"

        return res

    def PasswordCheck(self, username, password):
        data = {'username': username}

        res = self.send('masterinfo', data)
        if len(res) > 0:
            userinfo = res[0]
            if userinfo.get('username').__eq__(username):
                passwd = userinfo.get('password')
                checkpw = bcrypt.checkpw(password.encode('utf-8'), passwd.encode('utf-8'))
                return checkpw

        return False


    @restbase.gqlclient
    def CheckToken(self, token, client, app):
        isvalid = False
        userid = None
        groupid = -1
        authentication = None
        try:
            resp = client.checktoken_request(token)
            if 'check_token' in resp:
                respData = resp.get('check_token')
                if respData is not None:
                    isvalid = respData.get('isvalid')
                    userid = respData.get('user_id')
                    groupid = respData.get('group_id')
                    authentication = respData.get('authentication')
        except Exception as e:
            if app is not None:
                app.logger.info("{}".format(e))
            # else:
            #     return "EXCEPTION GETTOKEN : {}".format(e)

        return isvalid, userid, groupid, authentication

    @restbase.gqlclient
    def GetToken(self, username, password, client, app):
        token = None
        try:
            resp = client.login_request(username, password)
            if resp.get("login") is not None:
                token = resp.get("login").get("token")
        except Exception as e:
            if app is not None:
                app.logger.info("{}".format(e))
            # else:
            #     return "EXCEPTION GETTOKEN : {}".format(e)
        if app is not None:
            app.logger.info("token : {}".format(token))
        return token

    @restbase.gqlclient
    def GetNodeList(self, token, client, app):
        nodelist = None
        try:
            resp = client.nodelist_request(token)

            if resp.get("node_list") is not None:
                nodelist = resp.get("node_list").get("nodes")
        except Exception as e:
            if app is not None:
                app.logger.info("{}".format(e))
        if app is not None:
            app.logger.info("nodelist : {}".format(nodelist))
        return nodelist

    @restbase.gqlclient
    def GetVolumeList(self, token, client, app):
        volumelist = None
        try:
            resp = client.volumelist_request(token)
            if resp.get("volume_list") is not None:
                volumelist = resp.get("volume_list").get("volume")
        except Exception as e:
            if app is not None:
                app.logger.info("{}".format(e))
        if app is not None:
            app.logger.info("volumelist : {}".format(volumelist))
        return volumelist



