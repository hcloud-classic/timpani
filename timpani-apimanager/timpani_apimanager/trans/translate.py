import nameko
from nameko.rpc import RpcProxy

class RpcClient():

    def __init__(self, client_proc):
        self.client = client_proc

    def db_send(self, method, msg):
        # response = self.client.registerNode.call_aync(msg)
        # return response
        call_method = getattr(self.client,method)
        response = call_method.call_async(msg)
        return response