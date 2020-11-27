import graphene
from timpani_gateway.schema.fields import (ResponseMessageField, NodeField,
                                           ErrorResponse, IpmiConnResponse,
                                           NodeRequestField)

NodeUnion = type('NodeUnion', (graphene.Union,), {
    "Meta": type("Meta", (), {
        "types": (ResponseMessageField, NodeField)
    })
})

NodeRequestUnion = type("NodeRequestUnion",(graphene.Union, ),{
    "Meta":type("Meta",(),{
        "types": (ResponseMessageField, NodeField)
    })
})

IpmiConnUnion = type("IpmiConnUnion", (graphene.Union,), {
    "Meta":type("Meta", (),{
        "types": (ErrorResponse, IpmiConnResponse)
    })
})