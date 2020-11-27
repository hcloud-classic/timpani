import graphene

from ..union import NodeUnion, NodeRequestUnion
from ..fields import NodeRequestField, NodeField
from .node import resolve_getnode

class Query(graphene.ObjectType):
    node = graphene.Field(
        type = NodeField,
        uuid = graphene.String(default_value=None),
        resolver=resolve_getnode)