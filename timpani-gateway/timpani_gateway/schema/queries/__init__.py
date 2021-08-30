import graphene

from ..union import NodeUnion, NodeRequestUnion
from ..fields import NodeRequestField, NodeField, RegiManageNode, GetManageNode, CheckTokenResponse, LoginResponse, ValidResponse
from .node import resolve_getnode, resolve_updatenode
from .managenode import resolve_regmanagenode, resolve_getmanagenode
from .auth import resolve_login, resolve_checktoken, resolve_datasyncnoty, resolve_mastersync


class Query(graphene.ObjectType):
    node = graphene.Field(
        type=NodeField,
        uuid=graphene.String(default_value=None),
        resolver=resolve_getnode)

    updatenode = graphene.Field(
        type=graphene.String,
        uuid=graphene.String(default_value=None),
        nodeType=graphene.String(default_value=None),
        ipmiIp=graphene.String(default_value=None),
        ipmiPw=graphene.String(default_value=None),
        ipmiUser=graphene.String(default_value=None),
        resolver=resolve_updatenode
    )

    # Management Node List
    regmanagenode = graphene.Field(
        type=RegiManageNode,
        userId=graphene.String(),
        nodeList=graphene.List(graphene.String),
        resolver=resolve_regmanagenode

    )

    getmanagenode = graphene.Field(
        type=GetManageNode,
        userId=graphene.String(),
        resolver=resolve_getmanagenode
    )

    # AUTHORIZATION
    login = graphene.Field(
        type=LoginResponse,
        userId=graphene.String(),
        passwd=graphene.String(),
        resolver=resolve_login
    )

    checktoken = graphene.Field(
        type=CheckTokenResponse,
        token=graphene.String(),
        resolver=resolve_checktoken
    )

    mastersync = graphene.Field(
        type=ValidResponse,
        token=graphene.String(),
        username=graphene.String(),
        oldpw=graphene.String(),
        newpw=graphene.String(),
        resolver=resolve_mastersync
    )

    datasyncnoty = graphene.Field(
        type=ValidResponse,
        token=graphene.String(),
        synctype=graphene.String(),
        resolver=resolve_datasyncnoty
    )




