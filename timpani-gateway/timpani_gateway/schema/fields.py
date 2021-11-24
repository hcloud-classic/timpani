import graphene

class AccountField(graphene.ObjectType):
    id = graphene.String()
    username = graphene.String()
    register_on = graphene.String()

class NodeResponse(graphene.ObjectType):
    nodeuuid = graphene.String()

class ResponseMessageField(graphene.ObjectType):
    result = graphene.String()
    resultMessage = graphene.String()
    resultData = graphene.Field(NodeResponse)

class IpmiField(graphene.ObjectType):
    user = graphene.String()
    password = graphene.String()
    ipv4addr = graphene.String()
    ipv4port = graphene.String()

class NodeField(graphene.ObjectType):
    nodeuuid = graphene.String()
    capability = graphene.String()
    capabilitycode = graphene.String()
    nodealias = graphene.String()
    nodeuuid = graphene.String()
    ipmiinfo = IpmiField()

class ErrorField(graphene.ObjectType):
    errcode = graphene.String()
    errmsg = graphene.String()


class NodeRequestField(graphene.ObjectType):
    uuid = graphene.String()

class GetNodeResults(graphene.ObjectType):
    nodes = graphene.List(of_type = NodeField)


class ErrorResponse(graphene.ObjectType):
    resultcode = graphene.String()
    errormsg = graphene.String()

# IPMI Response Filed
class IpmiConnTest(graphene.ObjectType):
    result = graphene.String()
    ipv4address = graphene.String()
    ipmiconnid = graphene.String()

class IpmiConnResponse(graphene.ObjectType):
    resultcode = graphene.String()
    errorcode = graphene.String()
    errormsg = graphene.String()
    msg = graphene.List(of_type= IpmiConnTest)


###################### USER NODE MANAGEMENET ###########################

# return : {'user_id': <String>, 'insert_ok_cnt': <INT>, 'node_uuid_ok_list': [<String>,...,<String>]}
# return : {'user_id': <String>, 'node_cnt': <INT> ,'node_list': [<String>,...,<String>]}
class RegiManageNode(graphene.ObjectType):
    userId = graphene.String()
    nodeOkCnt = graphene.Int()
    nodeOkList = graphene.List(graphene.String)


class GetManageNode(graphene.ObjectType):
    userId = graphene.String()
    nodeCnt = graphene.Int()
    nodeList = graphene.List(graphene.String)


class CheckTokenResponse(graphene.ObjectType):
    isvalid = graphene.Boolean()
    userId = graphene.String()
    groupId = graphene.Int()
    authentication = graphene.String()

class LoginResponse(graphene.ObjectType):
    token = graphene.String()
    errors = graphene.Field(ErrorField)

class ValidResponse(graphene.ObjectType):
    isvalid = graphene.Boolean()
    errors = graphene.Field(ErrorField)

class CmdResponse(graphene.ObjectType):
    runstatus = graphene.String()
    runuuid = graphene.String()
    errors = graphene.Field(ErrorField)

class RealLogData(graphene.ObjectType):
    nodetype = graphene.String()
    usetype = graphene.String()
    name = graphene.String()
    start = graphene.String()
    status = graphene.String()
    kind = graphene.String()
    message = graphene.String()
    errmsg = graphene.String()
    errcode = graphene.String()


class RealLogResponse(graphene.ObjectType):
    proc = graphene.List(RealLogData)
    errors = graphene.Field(ErrorField)


class HistoryData(graphene.ObjectType):
    nodetype = graphene.String()
    usetype = graphene.String()
    uuid = graphene.String()
    kind = graphene.String()
    status = graphene.String()
    startat = graphene.String()
    endat = graphene.String()
    name = graphene.String()
    message = graphene.String()


class HistoryResponse(graphene.ObjectType):
    logs = graphene.List(HistoryData)
    errors = graphene.Field(ErrorField)


class RestoreTargetData(graphene.ObjectType):
    usetype = graphene.String()
    nodetype = graphene.String()
    snapname = graphene.String()
    snapfilename = graphene.String()
    target_uuid = graphene.String()
    name = graphene.String()
    time = graphene.String()
    isfull = graphene.Int()
    islast = graphene.Int()
    isrollback = graphene.String()


class RestoretargetListResponse(graphene.ObjectType):
    targets = graphene.List(RestoreTargetData)
    errors = graphene.Field(ErrorField)


class BackupTargetData(graphene.ObjectType):
    uuid = graphene.String()
    nodetype = graphene.String()
    name = graphene.String()
    usetype = graphene.String()
    backuptype = graphene.String()


class BackupTargetResponse(graphene.ObjectType):
    targets = graphene.List(BackupTargetData)
    errors = graphene.Field(ErrorField)

