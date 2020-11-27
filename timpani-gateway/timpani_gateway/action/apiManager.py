from nameko.standalone.rpc import ClusterRpcProxy
from functools import partial

class ApiManager:

    def __init__(self, amqp_url):
        self.config = {'AMQP_URI':amqp_url}

    def test_api(self,ip):
        print("test_api : ip = {}".format(ip))
        return "SUCCESS"

    def test(self,**kwargs):
        res = self.send(test,**kwargs)
        return res

    def send(self,method_name,**kwargs):

        # with ClusterRpcProxy(self.config) as rpc:
        #     func = "rpc.timpaniApiManager.call_async{}".format(method_name)
        func = "self.{}".format(method_name)
        func_res = partial(lambda f: func,kwargs)
        # result = lambda func:func(kwargs)
        result = func_res()

        return result

    # All Node List
    def gw_getNodeList(self):
        node_list = self.api_manager.getNodeList
        return node_list

if __name__=="__main__":
    test = ApiManager("aaaaa")
    res = test.test(ip="aaaa")
    print(res)
