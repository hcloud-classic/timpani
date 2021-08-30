import logging
import timpani_apimanager.service

logger = logging.getLogger(__name__)
#
# class NodeAPI(object):
#
#
#     def registerNode(self, data):
#         logger.info('RegisterNode {}'.format(data))
#         response = timpani_base.service.ApimanagerService.handler(method='registerNode', msg=data)
#         return response
#
#
#     # All Node List
#     def getNodeList(self, data):
#         logger.info("getNodeList {}".format(data))
#         response = self.client.handler(method='getNodeList', msg=data)
#         return response
#
#     # Leader Node List
#     def getNodeLeaderList(self, data):
#         logger.info("getNodeLeaderList {}".format(data))
#         response = self.client.handler(method='getNodeLeaderList', msg=data)
#         return response
#
#
#     # Compute Node List
#     def getNodeComputeList(self, data):
#         logger.info("getNodeComputeList nodeuuid : {}".format(data.get('nodeuuid')))
#         response = self.client.handler(method='getNodeComputeList', msg=data)
#         return response
#
#
#     # Get Node Info
#     def getNodeInfo(self, data):
#         logger.info("getNodeInfo nodeuuid : {}".format(data.get('nodeuuid')))
#         response = self.client.handler(method='getNodeInfo', msg=data)
#         return response
#
#
#     # Updete Node
#     def updateNode(self, data):
#         logger.info("updateNode: nodeuuid : {}".format(data.get('nodeuuid')))
#         response = self.client.handler(method='updateNode', msg=data)
#         return response
#
#
#     # Delete Node Info
#     def deleteNode(self, data):
#         logger.info("deleteNode nodeuuid : {}".format(data.get('nodeuuid')))
#         response = self.client.handler(method='deleteNode', msg=data)
#         return response
