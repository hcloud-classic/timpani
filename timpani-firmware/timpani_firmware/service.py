from .apimanager_pb2 import ActionResponse, ResgisterResponse
from .apimanager_pb2_grpc import ApimangerServiceStub

from timpani_framework.grpc.entrypoint import Grpc
from google.protobuf import json_format
import json

grpc = Grpc.implementing(ApimangerServiceStub)


# ActionRequest
# int32 action = 1;
# int32 msgid = 2;
# string method = 3;
# google.protobuf.Struct message = 4;

class ApiManagerService:
    name = 'apimanager_service'

    @grpc
    def action(self, request, context):
        print('request : {}'.format(request))
        print('action : {}'.format(request.action))
        print('msgid : {}'.format(request.msgid))
        print('method : {}'.format(request.method))
        print('msg : {}'.format(json.loads(request.msg)))
        return ActionResponse(
            result='success',
            msgid=request.msgid,
            method=request.method,
            msg=request.msg
        )

    # @grpc
    # def register(self, request, context):
    #     return ResgisterResponse()

# import eventlet
# import errno
# import time
# from timpani_framework.runner import run_services
#
# def main():
#     config={}
#     api = ApiManagerService()
#
#     service_runner = run_services(config, api)
#
#     while True:
#         try:
#             time.sleep(60)
#         except KeyboardInterrupt:
#             print()
#             try:
#                 service_runner.stop()
#             except KeyboardInterrupt:
#                 print()
#                 service_runner.kill()
#
#             else:
#             # runner.wait completed
#                 break
#
# if __name__=="__main__":
#     main()
