import nameko
from nameko.standalone.rpc import ClusterRpcClient
from timpani_gateway.constants import AMQP_CONFIG

class ApimanagerClient():

    @nameko.config.patch(AMQP_CONFIG)
    def send(self, method, msg):
        print(AMQP_CONFIG['AMQP_URI'])
        with ClusterRpcClient() as rpc:
            call_method = getattr(rpc.apimanager_service, method)
            # res = call_method.call_async(msg)
            res = call_method(msg)
        return res
