import nameko
import datetime
import bcrypt
from ..jwt.jwt import jwtutil
from pytz import timezone
from nameko.standalone.rpc import ClusterRpcClient
from timpani_base.constants import NAMEKO_AMQP_URI
from timpani_base.constants import (SYNC_PROC, SYNC_PROC_HIST, SYNC_PROC_PARAM_NAME, SYNC_PROC_UPDATE,
                                    SYNC_PROC_PRE, SYNC_PROC_AFTER)
from ..rest_api.base import DataParser
from ..auth.passwdDecode import PasswdDecode
from ..constants import INTERNAL_TOKEN_LIST

class ApimanagerClient():

    restbase = DataParser()
    decoder = PasswdDecode()
    app = None

    def setapp(self, app):
        self.app = app
        self.restbase.setapp(app)
        self.decoder = PasswdDecode(app)

    @nameko.config.patch(NAMEKO_AMQP_URI)
    def send(self, method, msg):
        if self.app is not None:
            self.app.logger.info(NAMEKO_AMQP_URI['AMQP_URI'])

        with ClusterRpcClient() as rpc:
            call_method = getattr(rpc.apimanager_service, method)
            # res = call_method.call_async(msg)
            res = call_method(msg)
        return res

    @restbase.gqlclient
    def login(self, username, password, client, app):
        new_salt = bcrypt.gensalt()
        if password is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}
        if username is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}
        bcrypthash = bcrypt.hashpw(password.encode('utf-8'), new_salt)
        try:
            res = client.login_request(username, bcrypthash.decode('utf-8'))
            if 'login' in res:
                respdata = res.get('login')
                token = respdata.get("token")
                if token.__eq__('') or token is None:
                    err_code = "1002"
                    err_message = "Login Failed"
                    return {'err_code': err_code, 'err_message': err_message}
                isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)
                if authentication.upper.__eq__('MASTER'):
                    self.PasswordUpdate(username, password)
                return respdata
        except Exception as e:
            # Local Master Login Check
            checkpass = self.PasswordCheck(username, bcrypthash)
            if checkpass:
                jwt = jwtutil()
                token_b = jwt.createToken()
                if self.app:
                    self.app.logger.info("token_b : {} type : {}".format(token_b, type(token_b)))
                token = str(token_b, encoding='utf-8')
                issave = True
                for i_token in INTERNAL_TOKEN_LIST:
                    if i_token.__eq__(token):
                        issave = False

                if issave:
                    INTERNAL_TOKEN_LIST.append(token)

                if len(INTERNAL_TOKEN_LIST) > 10:
                    INTERNAL_TOKEN_LIST.pop(-1)

                if self.app:
                    self.app.logger.info("INTERNAL_TOKEN_LIST : {}".format(INTERNAL_TOKEN_LIST))
                return {'token': token}
        err_code = "1002"
        err_message = "Login Failed"
        return {'err_code': err_code, 'err_message': err_message}


    def backuptargetlist(self, data):
        token = data.get('token')
        usetype = data.get('usetype').upper()
        if token is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}
        if usetype is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}
        elif usetype.upper().__eq__('OS') or usetype.upper().__eq__('ORIGIN') or usetype.upper().__eq__('DATA') or usetype.upper().__eq__('ALL'):
            iscontinue = True
        else:
            iscontinue = False

        if not iscontinue:
            err_code = "1004"
            err_message = "Parameter Data miss matching"
            return {'err_code': err_code, 'err_message': err_message}

        if self.app is not None:
            self.app.logger.info("dic_data : {}".format(token))
        try:
            isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)

            resdata = {
                'targets': []
            }

            if isvalid:
                if isinternal:
                    nodelist = self.LocalNodeList()
                    volumelist = self.LocalVolumeList()
                else:
                    nodelist = self.GetNodeList(token)
                    volumelist = self.GetVolumeList(token)
            else:
                err_code = "1003"
                err_message = "Token Check Failed"
                return {'err_code': err_code, 'err_message': err_message}

            if authentication.upper().__eq__('MASTER'):
                targets = resdata.get('targets')
                for nodedata in nodelist:
                    nodetype = nodedata.get('node_name').upper()
                    uuid = nodedata.get('uuid').upper()
                    if nodetype.__eq__('MASTER') or nodetype.__eq__('STORAGE'):
                        if nodetype.__eq__('MASTER'):
                            if usetype.__eq__('OS') or usetype.__eq__('ALL'):
                                target = {
                                    'uuid': uuid,
                                    'usetype': 'OS',
                                    'name': '/',
                                    'backuptype': 'FULL',
                                    'nodetype': nodetype
                                }
                                targets.append(target)
                            if usetype.__eq__('ORIGIN') or usetype.__eq__('ALL'):
                                target = {
                                    'uuid': uuid,
                                    'usetype': 'ORIGIN',
                                    'name': '/',
                                    'backuptype': 'FULL',
                                    'nodetype': nodetype
                                }
                                targets.append(target)
                            if usetype.__eq__('DATA') or usetype.__eq__('ORIGIN') or usetype.__eq__('ALL'):
                                data_find = {'uuid': uuid.replace('-','').upper()}
                                try:
                                    datares = self.send('getdatadir', data_find)
                                    if datares is not None:
                                        if len(datares) > 0:
                                            for masterdata in datares:
                                                datauuid = masterdata.get('uuid')
                                                datadir = masterdata.get('name')
                                                if usetype.__eq__('DATA') or usetype.__eq__('ALL'):
                                                    if datauuid.upper().__eq__(uuid.replace('-','').upper()):
                                                        target = {
                                                            'uuid': uuid,
                                                            'usetype': 'DATA',
                                                            'name': datadir,
                                                            'backuptype': 'INCREMENT',
                                                            'nodetype': nodetype
                                                        }
                                                        targets.append(target)
                                                if usetype.__eq__('ORIGIN') or usetype.__eq__('ALL'):
                                                    if datauuid.upper().__eq__(uuid.replace('-', '').upper()):
                                                        target = {
                                                            'uuid': uuid,
                                                            'usetype': 'ORIGIN',
                                                            'name': datadir,
                                                            'backuptype': 'FULL',
                                                            'nodetype': nodetype
                                                        }
                                                        targets.append(target)

                                except :
                                    if self.app is not None:
                                        self.app.logger.info("DATA DIR INFORMATION NOT FOUND")


                        if nodetype.__eq__('STORAGE') :
                            if usetype.__eq__('OS') or usetype.__eq__('ORIGIN') or usetype.__eq__('ALL'):
                                try:
                                    data_find = {'uuid': uuid.replace('-', '').upper()}
                                    datares = self.send('getdatadir', data_find)
                                    if datares is not None:
                                        if len(datares) > 0:
                                            for masterdata in datares:
                                                datauuid = masterdata.get('uuid')
                                                datausetype = masterdata.get('usetype')
                                                datadir = masterdata.get('name')
                                                if usetype.__eq__('OS') or usetype.__eq__('ALL'):
                                                    if datausetype.upper().__eq__('OS') and datauuid.upper().__eq__(uuid.replace('-','').upper()):
                                                        target = {
                                                            'uuid': uuid,
                                                            'usetype': 'OS',
                                                            'name': datadir,
                                                            'backuptype': 'FULL',
                                                            'nodetype': nodetype
                                                        }
                                                        targets.append(target)
                                                if usetype.__eq__('ORIGIN') or usetype.__eq__('ALL'):
                                                    if datausetype.upper().__eq__('OS') and datauuid.upper().__eq__(uuid.replace('-','').upper()):
                                                        target = {
                                                            'uuid': uuid,
                                                            'usetype': 'ORIGIN',
                                                            'name': datadir,
                                                            'backuptype': 'FULL',
                                                            'nodetype': nodetype
                                                        }
                                                        targets.append(target)

                                except:
                                    if self.app is not None:
                                        self.app.logger.info("DATA DIR INFORMATION NOT FOUND")
                    else:
                        for volumedata in volumelist:
                            kind = volumedata.get('use_type').upper()
                            uuid = volumedata.get('server_uuid').upper()
                            name = volumedata.get('name')
                            if kind.__eq__('OS'):
                                backuptype = 'FULL'
                            else:
                                backuptype = 'INCREMENT'

                            if nodedata.get('server_uuid').upper().__eq__(uuid):
                                nodetype = nodedata.get('node_name').upper()
                                uuid = nodedata.get('uuid')
                                if nodetype.__eq__('COMPUTE'):
                                    backuptype = 'INCREMENT'
                                target = {
                                    'uuid': uuid,
                                    'usetype': kind,
                                    'name': name,
                                    'backuptype': backuptype,
                                    'nodetype': nodetype
                                }
                                targets.append(target)
            else:
                targets = resdata.get('targets')

                for volumedata in volumelist:

                    kind = volumedata.get('use_type').upper()
                    uuid = volumedata.get('server_uuid').upper()
                    name = volumedata.get('name')
                    if kind.__eq__('OS'):
                        backuptype = 'FULL'
                    else:
                        backuptype = 'INCREMENT'

                    for nodedata in nodelist:
                        if nodedata.get('server_uuid').upper().__eq__(uuid):
                            nodetype = nodedata.get('node_name').upper()
                            uuid = nodedata.get('uuid')
                            if nodetype.__eq__('COMPUTE'):
                                backuptype = 'INCREMENT'
                            target = {
                                'uuid': uuid,
                                'usetype': kind,
                                'name': name,
                                'backuptype': backuptype,
                                'nodetype': nodetype
                            }
                            targets.append(target)
        except Exception as e:
            if self.app is not None:
                self.app.logger.info("EXCEPTION : {}".format(e))
            err_code = "1003"
            err_message = "Token Check Failed"
            return {'err_code': err_code, 'err_message': err_message}

        return targets

    def decodepasswd(self, passwd):
        decoder = PasswdDecode(self.app)
        pw = decoder.decode(passwd, ishex=False)
        return pw

    def mastersync(self, username, password):
        decoder = PasswdDecode(self.app)
        if self.app is not None:
            self.app.logger.info("user : {} password : {}".format(username, password))
        sha256_passwd = decoder.decode(password)
        if sha256_passwd is None:
            err_code = "1006"
            err_message = "Password Check Failed"
            return {'err_code': err_code, 'err_message': err_message}
        if self.app is not None:
            self.app.logger.info("sha256 password : {}".format(sha256_passwd))
        # Login Test
        new_salt = bcrypt.gensalt()
        bcrypthash = bcrypt.hashpw(sha256_passwd.encode('utf-8'), new_salt)
        token = self.GetToken(username, bcrypthash.decode('utf-8'))
        if token is not None:
            # password : chacha20-poly1305
            msg = {'username': username, 'password': sha256_passwd}
            if self.app is not None:
                self.app.logger.info("username  : {}, decode password : {}".format(username, sha256_passwd))
            res = self.send("mastersync", msg)
            if self.app is not None:
                self.app.logger.info("res : {}".format(res))
            if 'errorcode' in res:
                err_code = "5500"
                err_message = "Internal DB Error"
                return {'err_code': err_code, 'err_message': err_message}
            elif res < 1:
                return {'isvalid': False}
            return {'isvalid': True}
        else:
            err_code = "1006"
            err_message = "Password Check Failed"
            return {'err_code': err_code, 'err_message': err_message}

    @restbase.gqlclient
    def sync_login(self, username, password, client, app):
        new_salt = bcrypt.gensalt()
        if password is None:
            return None
        if username is None:
            return None
        bcrypthash = bcrypt.hashpw(password.encode('utf-8'), new_salt)
        res = client.login_request(username, bcrypthash.decode('utf-8'))
        if 'login' in res:
            respdata = res.get('login')
            token = respdata.get("token")
            return token
        return None

    def InternalSend(self, data, sync_proc):
        self.app.logger.info("data : {} \nsync_proc:{}".format(data, sync_proc))
        is_err = False
        res = None
        try:
            res = self.send(method='synccheck', msg=data)
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

    def synccheck(self, sync_name):

        sync_proc_list = SYNC_PROC
        check_result = True
        is_error = False
        start_at = datetime.datetime.now(tz=timezone('Asia/Seoul'))
        data = {}
        # start_at = datetime.datetime.now(tz=timezone('UTC'))

        try:
            for sync_proc in SYNC_PROC:
                check_data = {SYNC_PROC_PARAM_NAME: sync_proc, 'sync_name': sync_name}
                if sync_proc.__eq__(SYNC_PROC_PRE):
                    self.app.logger.info("sync_proc:{}".format(SYNC_PROC_PRE))
                    # get master account information
                    data['masterinfo_list'] = self.send('masterinfo', data)
                    self.app.logger.info("masterinfo_list : {}".format(data))

                elif sync_proc.__eq__(SYNC_PROC_UPDATE):
                    self.app.logger.info("sync_proc:{}".format(SYNC_PROC_UPDATE))
                    # get token
                    masterinfo_list = data.get('masterinfo_list')
                    token = None
                    for masterinfo in masterinfo_list:
                        username = masterinfo.get('username')
                        passwd = masterinfo.get('password')
                        token = self.sync_login(username, passwd)
                        if token is not None:
                            break
                    self.app.logger.info("\ntoken : {}\n\n".format(token))
                    if token is not None:
                        nodelist = self.GetNodeList(token)
                        # password decrypt
                        # for nodeinfo in nodelist:
                        #     decoder = PasswdDecode(self.app)
                        #     passwd = nodeinfo.get('ipmi_user_password')
                        #     ipmi_passwd = decoder.decode(passwd, ishex=False)
                        #     nodeinfo['ipmi_user_password'] = ipmi_passwd
                        volumelist = self.GetVolumeList(token)
                    else:
                        iserr = True
                    check_data['data'] = {'nodelist': nodelist, 'volumelist': volumelist}
                    self.app.logger.info("\nnodelist : {}\n\nvolumelist : {}\n\n".format(nodelist, volumelist))

                elif sync_proc.__eq__(SYNC_PROC_AFTER):
                    self.app.logger.info("sync_proc:{}".format(SYNC_PROC_AFTER))
                    check_data['sync_result'] = '1'
                    check_data['sync_start_at'] = start_at

                iscontinue, iserr, res = self.InternalSend(check_data, sync_proc)
                if iserr:
                    res = {'syncok': False}
                    break

                if not iscontinue:
                    self.app.logger.info('[{}] iscontinue False'.format(sync_proc))
                    res = {'syncok': False}
                    break
                self.app.logger.info('[{}] iscontinue True'.format(sync_proc))
                res = {'syncok': True}

        except Exception as e:
            self.app.logger.info("EXCEPTION : {}".format(e))
            check_result = False
            res = {'syncok': False}

        return res

    def logincheck(self, username, password):
        token = self.GetToken(username, password)
        if token is None:
            return "USER ACCOUNT MISSMATCHING"

        isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)
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
                if self.app:
                    self.app.logger.info("userinfo : {}, password : {}".format(userinfo, password))
                passwd = userinfo.get('password')
                checkpw = bcrypt.checkpw(passwd.encode('utf-8'), password)
                return checkpw

        return False

    def PasswordUpdate(self, username, sha256_passwd):
        data = {'username': username}

        res = self.send('masterinfo', data)
        if len(res) == 0:
            msg = {'username': username, 'password': sha256_passwd}
            if self.app is not None:
                self.app.logger.info("username  : {}, decode password : {}".format(username, sha256_passwd))
            res = self.send("mastersync", msg)
            if 'errorcode' in res:
                err_code = "5500"
                err_message = "Internal DB Error"
                return False
            elif res > 0:
                return True

        return False

    def GetBackupList(self, token):
        isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)
        if isinternal:
            nodelist = self.LocalNodeList()
            volumelist = self.LocalVolumeList()
        else:
            nodelist = self.GetNodeList(token)
            volumelist = self.GetVolumeList(token)

        return nodelist, volumelist, authentication, isvalid, userid, groupid

    def GetProcessHist(self, data):
        token = data.get('token')
        if token is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}

        isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)
        if not isvalid:
            err_code = "1003"
            err_message = "Token Check Failed"
            return {'err_code': err_code, 'err_message': err_message}
        del data['token']

        if isinternal:
            volumelist = self.LocalVolumeList()
        else:
            volumelist = self.GetVolumeList(token)

        if authentication.upper().__eq__('MASTER'):
            namelist = None
        else:
            namelist = []
            for volumedata in volumelist:
                name = volumedata.get('name')
                namelist.append(name)
            data['namelist'] = namelist
        try:
            res = self.send(method='getprocesshist', msg=data)
            if 'errcode' in res:
                err_code = res.get('errcode')
                err_message = res.get('errstr')
                return {'err_code': err_code, 'err_message': err_message}
        except Exception as e:
            err_code = '1404'
            err_message = "Internal Error"
            return {'err_code': err_code, 'err_message': err_message}
        return res

    def GetRestoreList(self, data):
        token = data.get('token')
        usetype = data.get('usetype').upper()

        if token is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}
        if usetype is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}
        elif usetype.upper().__eq__('OS') or usetype.upper().__eq__('ORIGIN') or usetype.upper().__eq__('DATA') or usetype.upper().__eq__('ALL'):
            iscontinue = True
        else:
            iscontinue = False

        if not iscontinue:
            err_code = "1004"
            err_message = "Parameter Data miss matching"
            return {'err_code': err_code, 'err_message': err_message}

        if self.app is not None:
            self.app.logger.info("GetRestoreList token : {}\nusetype:{}\n".format(token, usetype))
        isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)

        if isvalid:
            # nodelist = self.client.GetNodeList(token)
            if isinternal:
                volumelist = self.LocalVolumeList()
            else:
                volumelist = self.GetVolumeList(token)
        else:
            err_code = "1003"
            err_message = "Token Check Failed"
            return {'err_code': err_code, 'err_message': err_message}

        data['authtype'] = authentication

        if authentication.upper().__eq__('MASTER'):
            namelist = None
        else:
            namelist = []
            for volumedata in volumelist:
                issave = False
                use_type = volumedata.get('use_type').upper()
                if usetype.__eq__("OS"):
                    if usetype.__eq__(use_type):
                        issave = True
                elif usetype.__eq__("DATA"):
                    if usetype.__eq__(use_type):
                        issave = True
                elif usetype.__eq__("ALL"):
                    if use_type.__eq__("OS") or use_type.__eq__("DATA"):
                        issave = True

                if issave:
                    name = volumedata.get('name')
                    namelist.append(name)
            data['namelist'] = namelist
        if self.app is not None:
            self.app.logger.info("GetRestoreList SEND BEFORE")

        try:
            res = self.send(method='getrestorelist', msg=data)
            if 'errcode' in res:
                err_code = res.get('errcode')
                err_message = res.get('errstr')
                return {'err_code': err_code, 'err_message': err_message}
        except Exception as e:
            err_code = '1404'
            err_message = "Internal Error"
            return {'err_code': err_code, 'err_message': err_message}

        return res

    def getrealloghist(self, data):
        token = data.get('token')
        if token is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}

        isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)
        if not isvalid:
            err_code = "1003"
            err_message = "Token Check Failed"
            return {'err_code': err_code, 'err_message': err_message}
        del data['token']
        try:
            res = self.send(method='getrealhist', msg=data)
            if 'errcode' in res:
                err_code = res.get('errcode')
                err_message = res.get('errstr')
                return {'err_code': err_code, 'err_message': err_message}
        except Exception as e:
            err_code = '1404'
            err_message = "Internal Error"
            return {'err_code': err_code, 'err_message': err_message}
        return res

    def backupcmd(self, data):
        token = data.get('token')
        if token is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}

        isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)
        if not isvalid:
            err_code = "1003"
            err_message = "Token Check Failed"
            return {'err_code': err_code, 'err_message': err_message}
        del data['token']

        name = data.get('name')
        nodetype = data.get('nodetype')
        isexistname = False

        if nodetype.upper().__eq__('COMPUTE'):
            if isinternal:
                volumelist = self.LocalVolumeList()
            else:
                volumelist = self.GetVolumeList(token)

            for volumedata in volumelist:
                vol_name = volumedata.get('name')
                if vol_name is not None:
                    if vol_name.__eq__(name):
                        isexistname = True

            if not isexistname:
                err_code = "1004"
                err_message = "Parameter Data miss matching"
                return {'err_code': err_code, 'err_message': err_message}

        try:
            res = self.send(method='backupcmd', msg=data)
            if 'errcode' in res:
                err_code = res.get('errcode')
                err_message = res.get('errstr')
                return {'err_code': err_code, 'err_message': err_message}
        except Exception as e:
            if self.app is not None:
                self.app.logger.info('[BACKUPCMD] Exception e :\n {}'.format(e))
            err_code = '1404'
            err_message = "Internal Error"
            return {'err_code': err_code, 'err_message': err_message}
        return res

    def restorecmd(self, data):
        token = data.get('token')
        if token is None:
            err_code = "1001"
            err_message = "Parameter Data None"
            return {'err_code': err_code, 'err_message': err_message}

        isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)
        if not isvalid:
            err_code = "1003"
            err_message = "Token Check Failed"
            return {'err_code': err_code, 'err_message': err_message}
        del data['token']
        try:
            res = self.send(method='restorecmd', msg=data)
            if 'errcode' in res:
                err_code = res.get('errcode')
                err_message = res.get('errstr')
                return {'err_code': err_code, 'err_message': err_message}
        except Exception as e:
            err_code = '1404'
            err_message = "Internal Error"
            return {'err_code': err_code, 'err_message': err_message}
        return res

    def biosconfiglist(self, data):
        token = data.get('token')
        internal = data.get('internal')
        isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)
        nodelist = self.GetNodeList(token)
        find_nodelist = []
        for node in nodelist:
            nodetype = node.get('node_name').upper()
            if nodetype.__eq__('COMPUTE'):
                server_uuid = node.get('server_uuid')
                macaddr = node.get('bmc_mac_addr')
                find_nodelist.append({'uuid': server_uuid, 'macaddr': macaddr})

        return find_nodelist

    def dumpbiosconfig(self, data):
        token = data.get('token')
        macaddr = data.get('macaddr')
        internal = data.get('internal')
        isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)

        if isinternal:
            nodelist = self.LocalNodeList()
        else:
            nodelist = self.GetNodeList(token)
        # "uuid", "server_uuid", "node_name", "group_id", "group_name", "ipmi_user_id",
        # "ipmi_user_password", "bmc_ip", "bmc_ip_subnet_mask", "bmc_mac_addr", "pxe_mac_addr"
        data['ipmi'] = None
        if self.app is not None:
            self.app.logger.info("dumpbiosconfig\nisvalid:{}\nnodelist:{}".format(isvalid,nodelist))
        for nodedata in nodelist:
            issave = True
            if authentication.upper().__eq__('ADMIN'):
                node_groupid = nodedata.get('group_id')

                if isinstance(groupid,str):
                    int_groupid = int(groupid)
                else:
                    int_groupid = groupid

                if isinstance(node_groupid, str):
                    int_node_groupid = int(node_groupid)
                else:
                    int_node_groupid = node_groupid

                if int_groupid != int_node_groupid:
                    issave = False

            if issave:
                node_macaddr = nodedata.get('bmc_mac_addr')
                if macaddr.__eq__(node_macaddr):
                    data['ipmi'] = {'user':nodedata.get('ipmi_user_id'),
                                    'passwd': self.decodepasswd(nodedata.get('ipmi_user_password')),
                                    'ip':nodedata.get('bmc_ip'),
                                    'macaddr': nodedata.get('bmc_mac_addr')}
                    nodetype = nodedata.get('node_name')
                    if nodetype.upper().__eq__('COMPUTE'):
                        data['target_uuid'] = nodedata.get('server_uuid')
                    else:
                        data['target_uuid'] = nodedata.get('uuid')

        data['runkind'] = 'dump'
        res = self.send(method='biosconfig', msg=data)
        return res

    def setbiosconfig(self, data):
        token = data.get('token')
        macaddr = data.get('macaddr')
        internal = data.get('internal')
        match_kind = data.get('match_kind')
        name = data.get('name')
        if match_kind is None:
            err_code = "7001"
            err_message = "Template Setting impossible"
            return {'err_code': err_code, 'err_message': err_message}

        if name is None:
            err_code = "7002"
            err_message = "Template Setting Parameter Missing"
            return {'err_code': err_code, 'err_message': err_message}

        isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)
        if not isvalid:
            err_code = "1003"
            err_message = "Token Check Failed"
            return {'err_code': err_code, 'err_message': err_message}
        del data['token']


        if isinternal:
            nodelist = self.LocalNodeList()
        else:
            nodelist = self.GetNodeList(token)
        # "uuid", "server_uuid", "node_name", "group_id", "group_name", "ipmi_user_id",
        # "ipmi_user_password", "bmc_ip", "bmc_ip_subnet_mask", "bmc_mac_addr", "pxe_mac_addr"
        data['ipmi'] = None
        for nodedata in nodelist:
            issave = True
            if authentication.upper().__eq__('ADMIN'):
                node_groupid = nodedata.get('group_id')

                if isinstance(groupid,str):
                    int_groupid = int(groupid)
                else:
                    int_groupid = groupid

                if isinstance(node_groupid, str):
                    int_node_groupid = int(node_groupid)
                else:
                    int_node_groupid = node_groupid

                if int_groupid != int_node_groupid:
                    issave = False

            if issave:
                node_macaddr = nodedata.get('bmc_mac_addr')
                if macaddr.__eq__(node_macaddr):
                    data['ipmi'] = {'user':nodedata.get('ipmi_user_id'),
                                    'passwd': self.decodepasswd(nodedata.get('ipmi_user_password')),
                                    'ip':nodedata.get('bmc_ip'),
                                    'macaddr': nodedata.get('bmc_mac_addr')}
                    nodetype = nodedata.get('node_name')
                    if nodetype.upper().__eq__('COMPUTE'):
                        data['target_uuid'] = nodedata.get('server_uuid')
                    else:
                        data['target_uuid'] = nodedata.get('uuid')

        if data['ipmi'] is None:
            err_code = "7002"
            err_message = "Template Setting Parameter Missing"
            return {'err_code': err_code, 'err_message': err_message}

        data['runkind'] = 'set'
        res = self.send(method='biosconfig', msg=data)
        return res

    def curtemplate(self, data):
        token = data.get('token')
        macaddr = data.get('macaddr')
        internal = data.get('internal')
        isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)

        if isinternal:
            nodelist = self.LocalNodeList()
            volumelist = self.LocalVolumeList()
        else:
            nodelist = self.GetNodeList(token)
            volumelist = self.GetVolumeList(token)
        # "uuid", "server_uuid", "node_name", "group_id", "group_name", "ipmi_user_id",
        # "ipmi_user_password", "bmc_ip", "bmc_ip_subnet_mask", "bmc_mac_addr", "pxe_mac_addr"
        data['ipmi'] = None
        server_uuid = None
        macaddrlist = []
        if authentication.upper().__eq__('USER'):
            for volumeinfo in volumelist:
                if userid.__eq__.volumeinfo.get('user_uuid'):
                    server_uuid = volumeinfo.get('server_uuid')
                    break

        for nodedata in nodelist:
            issave = True
            if authentication.upper().__eq__('ADMIN'):
                node_groupid = nodedata.get('group_id')

                if isinstance(groupid,str):
                    int_groupid = int(groupid)
                else:
                    int_groupid = groupid

                if isinstance(node_groupid, str):
                    int_node_groupid = int(node_groupid)
                else:
                    int_node_groupid = node_groupid

                if int_groupid != int_node_groupid:
                    issave = False

            if server_uuid is not None:
                if server_uuid.__eq__.nodedata.get('server_uuid'):
                    issave = True
                else:
                    issave = False

            if issave:
                node_macaddr = nodedata.get('bmc_mac_addr')
                nodetype = nodedata.get('node_name')
                if nodetype.upper().__eq__('COMPUTE'):
                    target_uuid = nodedata.get('server_uuid')
                else:
                    target_uuid = nodedata.get('uuid')
                save_data = {'uuid':target_uuid, 'macaddr': node_macaddr}
                macaddrlist.append(save_data)

        res = self.send(method='getcurtemplate', msg=macaddrlist)
        return res

    def getsyscfgdumplist(self, data):
        token = data.get('token')
        # macaddr = data.get('macaddr')
        # internal = data.get('internal')
        if self.app is not None:
            self.app.logger.info("[getsyscfgdump] token : {}".format(token))
        isvalid, userid, groupid, authentication, isinternal = self.CheckToken(token)

        if isinternal:
            nodelist = self.LocalNodeList()
            volumelist = self.LocalVolumeList()
        else:
            nodelist = self.GetNodeList(token)
            volumelist = self.GetVolumeList(token)
        # "uuid", "server_uuid", "node_name", "group_id", "group_name", "ipmi_user_id",
        # "ipmi_user_password", "bmc_ip", "bmc_ip_subnet_mask", "bmc_mac_addr", "pxe_mac_addr"
        data['ipmi'] = None
        server_uuid = None
        macaddrlist = []
        if authentication.upper().__eq__('USER'):
            for volumeinfo in volumelist:
                if userid.__eq__.volumeinfo.get('user_uuid'):
                    server_uuid = volumeinfo.get('server_uuid')
                    break

        for nodedata in nodelist:
            issave = True
            if authentication.upper().__eq__('ADMIN'):
                node_groupid = nodedata.get('group_id')

                if isinstance(groupid, str):
                    int_groupid = int(groupid)
                else:
                    int_groupid = groupid

                if isinstance(node_groupid, str):
                    int_node_groupid = int(node_groupid)
                else:
                    int_node_groupid = node_groupid

                if int_groupid != int_node_groupid:
                    issave = False

            if server_uuid is not None:
                if server_uuid.__eq__.nodedata.get('server_uuid'):
                    issave = True
                else:
                    issave = False

            if issave:
                node_macaddr = nodedata.get('bmc_mac_addr')
                nodetype = nodedata.get('node_name')
                if nodetype.upper().__eq__('COMPUTE'):
                    target_uuid = nodedata.get('server_uuid')
                else:
                    target_uuid = nodedata.get('uuid')
                save_data = {'uuid': target_uuid, 'macaddr': node_macaddr, 'getkind':data.get('getkind')}
                macaddrlist.append(save_data)

        res = self.send(method='getsyscfgdumplist_api', msg=macaddrlist)
        return res

    @restbase.gqlclient
    def CheckToken(self, token, client, app):
        isvalid = False
        userid = None
        groupid = -1
        authentication = None
        isinternal = False

        if self.app:
            self.app.logger.info("[TOKENCHECK] INTERNAL_TOKEN_LIST : {}".format(INTERNAL_TOKEN_LIST))
        # Local Token Check
        for i_token in INTERNAL_TOKEN_LIST:
            if i_token.__eq__(token):
                jwt = jwtutil()
                token_decode = {'user_id': None, 'group_id': None, 'authentication': None}
                try:
                    token_decode = jwt.tokenInfo(token)
                    isvalid = True
                except Exception as e:
                    self.app.logger.info(e)
                    isvalid = False
                userid = token_decode.get('user_id')
                groupid = token_decode.get('group_id')
                authentication = token_decode.get('authentication')
                isinternal = True

        if isinternal:
            return isvalid, userid, groupid, authentication, isinternal

        try:
            resp = client.checktoken_request(token)
            if 'check_token' in resp:
                respData = resp.get('check_token')
                if respData is not None:
                    isvalid = respData.get('isvalid')
                    userid = respData.get('user_id')
                    groupid = respData.get('group_id')
                    authentication = respData.get('authentication')
                    isinternal = False
        except Exception as e:
            if self.app is not None:
                app.logger.info("{}".format(e))

        return isvalid, userid, groupid, authentication, isinternal

    @restbase.gqlclient
    def GetToken(self, username, password, client, app):
        token = None
        if client is None:
            if self.app is not None:
                self.app("GQL CLIENT NONE")

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

    def LocalNodeList(self):
        data = None
        return self.send('getnodelist', data)

    def LocalVolumeList(self):
        data = None
        return self.send('getvolumelist', data)



