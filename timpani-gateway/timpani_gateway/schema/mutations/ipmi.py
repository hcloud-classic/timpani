from uuid import uuid4


from timpani_gateway.schema.fields import IpmiConnTest, ErrorResponse, IpmiConnResponse
from timpani_gateway.schema.union import IpmiConnUnion
from timpani_gateway.nameko.api import ApimanagerClient

import graphene
# from flask_graphql_auth import mutation_jwt_required, get_jwt_identity
apimanager_client = ApimanagerClient()

def send_api(method, msg):
    call_method = getattr(apimanager_client,method)
    response = call_method(msg)
    return response

class RegisterIpmiConnetionMutation(graphene.Mutation):

    class Arguments(object):
        ipv4address = graphene.String()
        ipv4port = graphene.String()
        user = graphene.String()
        passwd = graphene.String()

    result = graphene.Field(IpmiConnUnion)

    @staticmethod
    def mutate(root, info, **kwargs):
        msg = {}
        print("Mutation RegisterNode : root = (), info = {}, kwargs = {}".format(root,info, **kwargs))
        for k,v in kwargs.items():
            msg[k] = v
            print("kwargs {} = {}".format(k,v))
        response = send_api(method='test',msg=msg)
        print(response)
        error = False
        if error:
            return RegisterIpmiConnetionMutation(IpmiConnResponse(resultcode="0400",errorcode='E0401',errormsg="IPMI Connection Test Failed", msg=[]))
        else:
            res_list = []
            res_list.append(IpmiConnTest(result="1", ipv4address="172.32.2.1", ipmiconnid="1"))
            res_list.append(IpmiConnTest(result="0", ipv4address="172.32.2.2", ipmiconnid="2"))
            return RegisterIpmiConnetionMutation(IpmiConnResponse(resultcode="0000",errorcode='0000',errormsg="",msg=res_list))