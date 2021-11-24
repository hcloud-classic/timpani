from ..fields import CheckTokenResponse, LoginResponse, ValidResponse, ErrorField
from timpani_gateway.nameko.api import ApimanagerClient
from timpani_gateway.gql_client.GqlClient import GqlClient
from timpani_base.constants import QL_URL

apimanager_client = ApimanagerClient()

def resolve_login(root, info, user, passwd):
    res_data = LoginResponse()
    client = GqlClient(QL_URL, None)
    res = apimanager_client.login(user, passwd)
    errors = ErrorField()
    if 'err_code' in res:
        errors.errcode = res.get('err_code')
        errors.errmsg = res.get('err_message')
        token = None
    else:
        errors.errcode = None
        errors.errmsg = None
        token = res.get('token')
    res_data.token = token
    res_data.errors = errors
    return res_data


def resolve_checktoken(root, info, token):
    res_data = CheckTokenResponse()
    client = GqlClient(QL_URL, None)

    res = client.checktoken_request(token)
    if 'check_token' in res:
        respData = res.get('check_token')
        if respData is not None:
            res_data.isvalid = respData.get('isvalid')
            res_data.userId = respData.get('user_id')
            res_data.groupId = respData.get('group_id')
            res_data.authentication = respData.get('authentication')

    return res_data


def resolve_mastersync(root, info, token, username, newpw):
    res_data = ValidResponse()
    res = apimanager_client.mastersync(username, newpw)
    errors = ErrorField()
    if 'err_code' in res:
        errors.errcode = res.get('err_code')
        errors.errmsg = res.get('err_message')
        res_data.isvalid = False
        res_data.errors = errors
        return res_data

    errors.errcode = None
    errors.errmsg = None
    res_data.errors = errors
    res_data.isvalid = res.get('isvalid')

    return res_data


def resolve_datasyncnoty(root, info, token, synctype):
    res_data = ValidResponse()
    # client = GqlClient(QL_URL, None)
    res = None
    # res = client.login_request(username, newpw)
    if 'login' in res:
        respData = res.get('login')
        if respData is not None:
            res_data.token = respData.get('token')
    return res_data

