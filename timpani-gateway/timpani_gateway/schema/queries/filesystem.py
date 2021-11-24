from ..fields import (CheckTokenResponse, LoginResponse, ValidResponse, ErrorField,
                      CmdResponse, HistoryResponse, HistoryData, RealLogResponse, RealLogData,
                      RestoreTargetData, RestoretargetListResponse,BackupTargetData, BackupTargetResponse)
from timpani_gateway.nameko.api import ApimanagerClient
from timpani_gateway.gql_client.GqlClient import GqlClient

apimanager_client = ApimanagerClient()

def resolve_backuptargetlist(root, info, token, usetype):
    res_data = BackupTargetResponse
    data = {'token':token, 'usetype': usetype}
    res = apimanager_client.backuptargetlist(data)
    errors = ErrorField()
    if 'err_code' in res:
        errors.errcode = res.get('err_code')
        errors.errmsg = res.get('err_message')
        res_data.targets = None
        res_data.errors = errors
        return res_data

    errors.errcode = None
    errors.errmsg = None
    res_data.errors = errors

    datalist = []
    for data in res:
        data_parse =  BackupTargetData(
            uuid= data.get('uuid'),
            nodetype= data.get('nodetype'),
            name= data.get('name'),
            usetype= data.get('usetype'),
            backuptype= data.get('backuptype')
        )
        datalist.append(data_parse)
    res_data.targets = datalist
    return res_data

def resolve_restoretargetlist(root, info, token, usetype):
    res_data = RestoretargetListResponse()

    dic_data = {'token':token, 'usetype':usetype}
    res = apimanager_client.GetRestoreList(dic_data)
    errors = ErrorField()
    if 'err_code' in res:
        errors.errcode = res.get('err_code')
        errors.errmsg = res.get('err_message')
        res_data.targets = None
        res_data.errors = errors
        return res_data

    errors.errcode = None
    errors.errmsg = None
    res_data.errors = errors

    datalist = []
    for data in res:
        data_parse = RestoreTargetData(
            usetype = data.get('usetype'),
            nodetype = data.get('nodetype'),
            snapname = data.get('snapname'),
            snapfilename = data.get('snapfilename'),
            target_uuid = data.get('target_uuid'),
            name = data.get('name'),
            time = data.get('time'),
            isfull = data.get('isfull'),
            islast = data.get('islast'),
            isrollback = data.get('isrollback')
        )
        datalist.append(data_parse)
    res_data.targets = datalist
    return res_data

def resolve_backup(root, info, token, uuid, nodetype, usetype, name):
    resdata = CmdResponse()
    dic_data = {'token':token, 'uuid': uuid, 'nodetype': nodetype, 'usetype':usetype, 'name':name}
    res = apimanager_client.backupcmd(dic_data)
    errors = ErrorField()
    if 'err_code' in res:
        errors.errcode = res.get('err_code')
        errors.errmsg = res.get('err_message')
        resdata.runstatus = None
        resdata.runuuid = None
        resdata.errors = errors
        return resdata

    errors.errcode = None
    errors.errmsg = None
    resdata.errors = errors
    resdata.runstatus=res.get('runstatus')
    resdata.runuuid = res.get('runprocuuid')
    return resdata

def resolve_restore(root, info, token, snapname, usetype, nodetype, isboot):
    resdata = CmdResponse()
    dic_data = {'token': token, 'snapname': snapname, 'usetype': usetype, 'nodetype':nodetype, 'isboot':isboot}

    res = apimanager_client.restorecmd(dic_data)
    errors = ErrorField()
    if 'err_code' in res:
        errors.errcode = res.get('err_code')
        errors.errmsg = res.get('err_message')
        resdata.runstatus = None
        resdata.runuuid = None
        resdata.errors = errors
        return resdata

    errors.errcode = None
    errors.errmsg = None
    resdata.errors = errors
    resdata.runstatus = res.get('runstatus')
    resdata.runuuid = res.get('runprocuuid')
    return resdata


def resolve_reallog(root, info, token, runuuid):
    resdata = RealLogResponse()
    dic_data = {'token': token, 'run_uuid': runuuid}
    res = apimanager_client.send(method='getrealhist', msg=dic_data)
    errors = ErrorField()
    if 'err_code' in res:
        errors.errcode = res.get('err_code')
        errors.errmsg = res.get('err_message')
        res.proc = []
        res.errors = errors
        return resdata
    errors.errcode = None
    errors.errmsg = None
    resdata.errors = errors
    datalist = []
    for data in res:
        data_parse = RealLogData()
        data_parse.kind = data.get('kind')
        data_parse.message = data.get('message')
        data_parse.name = data.get('name')
        data_parse.start = data.get('start')
        data_parse.status = data.get('status')
        data_parse.nodetype = data.get('nodetype')
        data_parse.usetype = data.get('usetype')
        data_parse.err_code = data.get('err_code')
        data_parse.err_message = data.get('err_message')
        datalist.append(data_parse)
    resdata.proc = datalist

    return resdata

def resolve_history(root, info, token, kind):
    resdata = HistoryResponse()
    # kind : restore, backup
    dic_data = {'kind': kind, 'token': token}
    res = apimanager_client.GetProcessHist(dic_data)
    errors = ErrorField()

    if 'err_code' in res:
        errors.errcode = res.get('err_code')
        errors.errmsg = res.get('err_message')
        res.logs = None
        res.errors = errors
        return resdata
    errors.errcode = None
    errors.errmsg = None
    resdata.errors = errors

    datalist = []
    for data in res:
        data_parse = HistoryData(
            nodetype= data.get('nodetype'),
            usetype= data.get('usetype'),
            uuid= data.get('uuid'),
            kind= data.get('kind'),
            status= data.get('status'),
            startat= data.get('startat'),
            endat= data.get('endat'),
            name= data.get('name'),
            message= data.get('message')
        )
        datalist.append(data_parse)
    resdata.logs = datalist

    return resdata
