import graphene

from ..union import NodeUnion, NodeRequestUnion
from ..fields import (NodeRequestField, NodeField, RegiManageNode, GetManageNode,
                      CheckTokenResponse, LoginResponse, ValidResponse,
                      CmdResponse, RealLogResponse, HistoryResponse, BackupTargetResponse,
                      RestoretargetListResponse
                      )
from .node import resolve_getnode, resolve_updatenode
from .managenode import resolve_regmanagenode, resolve_getmanagenode
from .auth import resolve_login, resolve_checktoken, resolve_datasyncnoty, resolve_mastersync
from .filesystem import (resolve_backup, resolve_backuptargetlist, resolve_history,
                         resolve_reallog, resolve_restore, resolve_restoretargetlist)



class Query(graphene.ObjectType):

    # AUTHORIZATION
    login = graphene.Field(
        type=LoginResponse,
        user=graphene.String(),
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

    backuptargetlist = graphene.Field(
        type=BackupTargetResponse,
        token=graphene.String(),
        usetype=graphene.String(),
        resolver=resolve_backuptargetlist
    )

    restoretargetlist = graphene.Field(
        type=RestoretargetListResponse,
        token=graphene.String(),
        usetype=graphene.String(),
        resolver=resolve_restoretargetlist
    )

    backup = graphene.Field(
        type=CmdResponse,
        token=graphene.String(),
        uuid=graphene.String(),
        usetype=graphene.String(),
        nodetype=graphene.String(),
        name=graphene.String(),
        resolver=resolve_backup
    )

    restore = graphene.Field(
        type=CmdResponse,
        token=graphene.String(),
        snapname=graphene.String(),
        usetype=graphene.String(),
        nodetype=graphene.String(),
        isboot=graphene.Boolean(),
        resolver=resolve_restore
    )

    reallog = graphene.Field(
        type=RealLogResponse,
        token=graphene.String(),
        runuuid=graphene.String(),
        resolver=resolve_reallog
    )

    history = graphene.Field(
        type=HistoryResponse,
        token=graphene.String(),
        kind=graphene.String(),
        resolver=resolve_history
    )













