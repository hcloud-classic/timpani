from marshmallow import Schema, fields, post_dump

class BaseSchema(Schema):
    @post_dump
    def null_to_empty_string(self,data):
        return{
            key: '' for key, value in data.items()
            if value is None
        }

class IpmiConn(BaseSchema):
    user = fields.Str(required=False)
    password = fields.Str(required=False)
    ipv4addr = fields.Str(required=False)
    ipv4port = fields.Str(required=False)

# New Node ADD
class RegisterNode_V1(BaseSchema):
    node_name = fields.Str(required=True)
    node_type = fields.Str(required=True)
    parent_uuid = fields.Str(required=False)
    page_msg = fields.Str(required=False)
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