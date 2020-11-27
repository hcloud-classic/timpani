import nameko
import logging
from nameko.standalone.rpc import ServiceRpcProxy
from .constants import AMQP_CONFIG

logger = logging.getLogger(__name__)

class TransferServiceManager():

    AMQP_URI = AMQP_CONFIG

    def __init__(self, amqp_uri):
        self.AMQP_URI = amqp_uri

    def send(self, method, service_name, msg):
        logger.info("[SEND] Service Name : {} AMQP_URI : {}".format(service_name, self.AMQP_URI))

        with ServiceRpcProxy(service_name, self.AMQP_URI) as rpc:
            call_method = getattr(rpc, method)
            response = call_method.call_async(msg)
            return response.result()

    # amqp_config = AMQP_CONFIG

    # @staticmethod
    # def set_amqp_config(amqp_uri):
    #     amqp_config = amqp_uri
    #
    # @nameko.config.patch(amqp_config)
    # def send(self, method, msg):
    #     print("amqp_uri : {}".format(self.amqp_config['AMQP_URI']))
    #     with ClusterRpcClient() as rpc:
    #         call_method = getattr(rpc.service_manager, method)
    #         # res = call_method.call_async(msg)
    #         res = call_method(msg)
    #     return res

