import nameko
import logging
from nameko.standalone.rpc import ClusterRpcClient
from timpani_base.constants import NAMEKO_AMQP_URI

logger = logging.getLogger(__name__)

class TransferServiceManager():

    @nameko.config.patch(NAMEKO_AMQP_URI)
    def db_send(self, method, msg):
        print(NAMEKO_AMQP_URI['AMQP_URI'])
        with ClusterRpcClient() as rpc:
            call_method = getattr(rpc.dbmanager_service, method)
            # res = call_method.call_async(msg)
            res = call_method(msg)
        return res

    @nameko.config.patch(NAMEKO_AMQP_URI)
    def api_send(self, method, msg):
        print(NAMEKO_AMQP_URI['AMQP_URI'])
        with ClusterRpcClient() as rpc:
            call_method = getattr(rpc.apimanager_service, method)
            # res = call_method.call_async(msg)
            res = call_method(msg)
        return res



