from __future__ import print_function

from timpani_dbmanager.dbmanager_pb2 import ActionRequest, ActionResponse
from timpani_dbmanager.dbmanager_pb2_grpc import DbmanagerServiceStub
from timpani_framework.grpc.constants import Cardinality
from timpani_framework.grpc.client import Client
from timpani_framework.grpc.errors import GrpcError
from timpani_framework.grpc.dependency_provider import GrpcProxy
#from timpani_base.service import ClientService
import json
import grpc
import copy

class dbmanagerClient:

    def __init__(self):
        self.url =  "//127.0.0.1"
        self.stub = DbmanagerServiceStub
        self.msgid = 0
        self.port = 50051
        self.channel = grpc.insecure_channel('127.0.0.1:[]'.format(self.port))
 #       self.client = ClientService()
        # self.stub = DbmanagerServiceStub(self.channel)
        # self.grpc = GrpcProxy(self.url, self.stub)

    def get_msgid(self):
        self.msgid = self.msgid+1
        return self.msgid

    # def send(self, action, method, msg_dict):
    #     try:
    #         with Client("//127.0.0.1", DbmanagerServiceStub) as client:
    #             request = ActionRequest(action=1, msgid=self.get_msgid(), method="test", msg=json.dumps(msg_dict))
    #             # client.start(request)
    #             responses_future = client.action.future(request)
    #             responses = responses_future.result()
    #             print(responses)
    #             # for response in responses:
    #             print("db msg : {}".format(responses.msg))
    #             print(responses.result)
    #             # client.stop(request)
    #     except grpc.RpcError as exc:
    #         state = exc._state
    #         responses = None
    #         # responses = GrpcError(state.code, state.details, state.debug_error_string)
    #
    #     return responses

    # def send(self, action, method, msg_dict):
    #     request = ActionRequest(action=1, msgid=self.get_msgid(), method="test", msg=json.dumps(msg_dict))
    #     responses = None
    #     print("================ [1]")
    #     try:
    #         print("channel instance : {}".format("True" if self.channel else "False"))
    #         response = self.stub.action(request)
    #         responses = copy.deepcopy(response)
    #         print("================ [3]")
    #     except Exception as exc:
    #         print("DB Connection ERROR : {}".format(exc))
    #
    #     return responses

    def test(self, action, msg, func):
        msg_dict = json.loads(msg)
        method="test1"
        return  func(action=action, method=method,msg_dict=msg_dict)
