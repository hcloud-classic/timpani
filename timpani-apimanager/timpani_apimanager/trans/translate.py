import nameko
from nameko.standalone.rpc import ClusterRpcClient
from timpani_base.constants import NAMEKO_AMQP_URI

class RpcClient():

    @nameko.config.patch(NAMEKO_AMQP_URI)
    def db_send(self, method, msg):
        print(NAMEKO_AMQP_URI['AMQP_URI'])
        with ClusterRpcClient() as rpc:
            call_method = getattr(rpc.dbmanager_service, method)
            # res = call_method.call_async(msg)
            res = call_method(msg)
        return res

    @nameko.config.patch(NAMEKO_AMQP_URI)
    def backup_send(self, service_uuid, method, msg):
        print(NAMEKO_AMQP_URI['AMQP_URI'])
        # service_name = "backup_service_{}".format(service_uuid)
        service_name = "{}".format(service_uuid)
        with ClusterRpcClient() as rpc:
            service_call = getattr(rpc, service_name)
            call_method = getattr(service_call, method)
            # res = call_method.call_async(msg)
            res = call_method(msg)
        return res

    @nameko.config.patch(NAMEKO_AMQP_URI)
    def restore_send(self, service_uuid, method, msg):
        print(NAMEKO_AMQP_URI['AMQP_URI'])
        # service_name = "backup_service_{}".format(service_uuid)
        service_name = "{}".format(service_uuid)
        with ClusterRpcClient() as rpc:
            service_call = getattr(rpc, service_name)
            call_method = getattr(service_call, method)
            # res = call_method.call_async(msg)
            res = call_method(msg)
        return res

    @nameko.config.patch(NAMEKO_AMQP_URI)
    def bios_send(self, service_uuid, method, msg):
        print(NAMEKO_AMQP_URI['AMQP_URI'])
        # service_name = "backup_service_{}".format(service_uuid)
        service_name = "{}".format(service_uuid)
        with ClusterRpcClient() as rpc:
            service_call = getattr(rpc, service_name)
            call_method = getattr(service_call, method)
            # res = call_method.call_async(msg)
            res = call_method(msg)
        return res