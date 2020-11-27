import graphene

from .node import RegisterNodeMutation, UpdateNodeMutation, DeleteNodeMutation
from .ipmi import RegisterIpmiConnetionMutation

class Mutation(graphene.ObjectType):
    noderegister = RegisterNodeMutation.Field()
    nodeupdate = UpdateNodeMutation.Field()
    nodedelete = DeleteNodeMutation.Field()
    ipmiconn = RegisterIpmiConnetionMutation.Field()