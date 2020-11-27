from uuid import uuid4


from timpani_gateway.schema.fields import ResponseMessageField, NodeResponse
from timpani_gateway.schema.union import NodeUnion
from timpani_gateway.nameko.api import ApimanagerClient

import graphene
# from flask_graphql_auth import mutation_jwt_required, get_jwt_identity
# apimanager_client = ApimanagerClient()

convert_map = {'nodeuuid':'node_uuid', 'nodename':'node_name', 'nodetype': 'node_type', 'parentuuid':'parent_uuid', 'ipmiinfo':'ipmi_info'}

# def send_api(method, msg):
#     response = apimanager_client.send(method=method, msg=msg)
#     call_method = getattr(apimanager_client, method)
    # response = call_method(msg)
    # return response

class IpmiField_input(graphene.InputObjectType):
    user = graphene.String()
    password = graphene.String()
    ipv4addr = graphene.String()
    ipv4port = graphene.String()

class RegisterNodeMutation(graphene.Mutation):


    class Arguments(object):
        nodeuuid = graphene.String()
        nodetype = graphene.String()
        nodename = graphene.String()
        parentuuid = graphene.String()
        ipmiinfo = IpmiField_input()



    result = graphene.Field(NodeUnion)

    @staticmethod
    def mutate(root, info, **kwargs):
        apimanager_client = ApimanagerClient()
        msg = {}
        print("Mutation RegisterNode : root = (), info = {}, kwargs = {}".format(root, info, **kwargs))

        for k,v in kwargs.items():
            if convert_map.get(k):
                key_value = convert_map.get(k)
            else:
                key_value = k
            msg[key_value] = v

            print("kwargs {} = {}".format(k,v))

        # response = {}
        response = apimanager_client.send(method='registerNode', msg=msg)
        print(response)
        if response.get('errorcode') is None:
            success_data = NodeResponse()
            success_data.nodeuuid = response.get('node_uuid')
            ret_data = ResponseMessageField(result="0000", resultMessage="Success", resultData=success_data)
        else:
            error_data = NodeResponse()
            error_data.nodeuuid = ""
            errorcode= response.get('errorcode')
            errorstr = response.get('errorstr')
            ret_data = ResponseMessageField(result=errorcode, resultMessage=errorstr, resultData=error_data)

        return RegisterNodeMutation(ret_data)

class UpdateNodeMutation(graphene.Mutation):


    class Arguments(object):
        nodeuuid = graphene.String()
        nodetype = graphene.String()
        nodename = graphene.String()
        parentuuid = graphene.String()
        ipmiinfo = IpmiField_input()

    result = graphene.Field(NodeUnion)

    @staticmethod
    def mutate(root, info, **kwargs):
        msg = {}
        print("Mutation RegisterNode : root = (), info = {}, kwargs = {}".format(root, info, **kwargs))
        for k, v in kwargs.items():
            if convert_map.get(k):
                key_value = convert_map.get(k)
            else:
                key_value = k
            msg[key_value] = v

            print("kwargs {} = {}".format(k,v))
        response = {}
        # response = send_api(method='test', msg=msg)
        print(response)
        success_data = NodeResponse()
        success_data.nodeuuid = "test_node_uuid"
        success = ResponseMessageField(result="0000", resultMessage="Success", resultData=success_data)
        error_data = NodeResponse()
        error_data.nodeuuid=""
        errorcode = "0400"
        errorstr = "ERROR TEST"
        error = ResponseMessageField(result=errorcode, resultMessage=errorstr, resultData=error_data)

        return RegisterNodeMutation(error)


class DeleteNodeMutation(graphene.Mutation):


    class Arguments(object):
        nodeuuid = graphene.String()

    result = graphene.Field(NodeUnion)

    @staticmethod
    def mutate(root, info, **kwargs):
        msg = {}
        print("Mutation RegisterNode : root = (), info = {}, kwargs = {}".format(root, info, **kwargs))
        for k, v in kwargs.items():
            if convert_map.get(k):
                key_value = convert_map.get(k)
            else:
                key_value = k
            msg[key_value] = v

            print("kwargs {} = {}".format(k,v))
        response = {}
        # response = send_api(method='test', msg=msg)
        print(response)
        success_data = NodeResponse()
        success_data.nodeuuid = "test_node_uuid"
        success = ResponseMessageField(result="0000", resultMessage="Success", resultData=success_data)
        errorcode="0400"
        errorstr = "ERROR TEST"
        error = ResponseMessageField(result=errorcode, resultMessage=errorstr, resultData=None)

        return RegisterNodeMutation(error)