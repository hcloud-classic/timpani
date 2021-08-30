from timpani_gateway.schema.fields import NodeField
from timpani_gateway.nameko.api import ApimanagerClient

apimanager_client = ApimanagerClient()

def resolve_getnode(root, info, **kwargs):
    node_uuid = kwargs.get('uuid', None)
    print("query resolve_getnode : root = (), info = {}, kwargs = {}".format(root, info, node_uuid))
    msg = {'node_uuid':node_uuid}
    apimanager_client.test(msg)
    node = None
    # node = NodeField(
    #     id='1',
    #     capability = 'Leader',
    #     capabilitycode = 'NL',
    #     nodealias = 'Test Leader Node',
    #     nodeuuid = 'uuid-01-02'
    # )

    return msg

def resolve_updatenode(root, info, **kwargs):
    uuid = kwargs.get('uuid')
    type = kwargs.get('nodeType')
    ipmiIp = kwargs.get('ipmiIp')
    ipmiPw = kwargs.get('ipmiPw')
    ipmiUser = kwargs.get('ipmiUser')
    msg={'node_uuid':uuid, 'node_type':type, 'ipmi_ipv4':ipmiIp, 'ipmi_user':ipmiUser, 'ipmi_passwd':ipmiPw}

    return msg