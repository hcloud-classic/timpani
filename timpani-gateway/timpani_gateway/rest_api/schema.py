from marshmallow import Schema, fields, post_dump

class BaseSchema(Schema):
    @post_dump
    def null_to_empty_string(self,data):
        return{
            key: '' for key, value in data.items()
            if value is None
        }

class Login(BaseSchema):
    user = fields.Str(required=True)
    password = fields.Str(required=True)


class CheckToken(BaseSchema):
    token = fields.Str(required=True)
    internal = fields.Str(required=False)

class IpmiConn(BaseSchema):
    user = fields.Str(required=False)
    password = fields.Str(required=False)
    ipv4addr = fields.Str(required=False)
    ipv4port = fields.Str(required=False)
    macaddr = fields.String(required=False)

# New Node ADD
class RegisterNode_V1(BaseSchema):
    node_name = fields.Str(required=False)
    node_type = fields.Str(required=True)
    parent_uuid = fields.Str(required=False)
    page_msg = fields.Str(required=False)
    node_uuid = fields.Str(required=False)
    service_ip = fields.String(required=False)
    service_mac = fields.String(required=False)
    ipmi_info = fields.Nested(IpmiConn)

class RegisterNode(BaseSchema):
    nodeuuid = fields.Str(required=True)
    nodealias = fields.Str(required=True)
    capability = fields.Str(required=True)   # Leader, Compute
    parentuuid = fields.Str(required=False)

class UpdateNode(BaseSchema):
    nodealias = fields.Str(required=True)
    capability = fields.Str(required=True)   # Leader, Compute
    parentuuid = fields.Str(required=False)

class ChildNode(BaseSchema):
    parent_uuid = fields.Str(required=True)

class GetBackupSrcList(BaseSchema):
    node_uuid = fields.Str(required=True)
    zfs_type_list = fields.List(fields.Str(), required=False)

class GetRecoverList(BaseSchema):
    node_uuid = fields.Str(required=True)

class SystemBackup(BaseSchema):
    node_uuid = fields.Str(required=True)       # target node uuid
    backup_type = fields.Str(required=True)
    backup_target = fields.List(fields.Str(), required=True)

class SystemRecover(BaseSchema):
    node_uuid = fields.Str(required=True)       # target node uuid
    recover_type = fields.Str(required=True)    # I, F, O\
    snapname = fields.Str(required=True)
    target_image = fields.List(fields.Str(), required=True)

class SystemHistory(BaseSchema):
    node_uuid = fields.Str(required=False)
    target_type_list = fields.List(fields.Str(), required=False)

class SetSystemHistory(BaseSchema):
    node_uuid = fields.Str(required=True)   # system uuid
    kind = fields.Str(required=False)
    action_kind = fields.Str(required=True) # action kind
    action_msg = fields.Str(required=True)  # action message [running step]
    action_err_code = fields.Str(required=False) # error code
    action_err_msg = fields.Str(required=False) # error message [error detail]
    action_status = fields.Str(required=True)   # action status [START, RUN, PASS, END]
    run_uuid = fields.Str(required=False)    # None : uuid generate [ START ]


class SyncCheck(BaseSchema):
    sync_name = fields.Str(required=True)

class Backup(BaseSchema):
    uuid = fields.Str(required=True)
    usetype = fields.Str()
    nodetype = fields.Str()
    name = fields.Str()

