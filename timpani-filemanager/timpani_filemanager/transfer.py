# import nameko
# import logging
# from nameko.standalone.rpc import ClusterRpcClient
# from timpani_filemanager.constants import AMQP_CONFIG
#
# logger = logging.getLogger(__name__)
#
# class TransferServiceManager(object):
#
#     @nameko.config.patch(AMQP_CONFIG)
#     def send(self, method, msg):
#         print(AMQP_CONFIG['AMQP_URI'])
#         with ClusterRpcClient() as rpc:
#             call_method = getattr(rpc.service_manager, method)
#             # res = call_method.call_async(msg)
#             res = call_method(msg)
#         return res

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