from timpani_gateway.schema.fields import RegiManageNode, GetManageNode
from timpani_gateway.nameko.api import ApimanagerClient

apimanager_client = ApimanagerClient()


# return : {'user_id': <String>, 'insert_ok_cnt': <INT>, 'node_uuid_ok_list': [<String>,...,<String>]}
# return : {'user_id': <String>, 'node_cnt': <INT> ,'node_list': [<String>,...,<String>]}

def resolve_regmanagenode(root, info, userId, nodeList):
    # user_id = kwargs.get('user_id', None)
    # node_list = kwargs.get('node_list', None)
    print("query resolve_regmanagenode : root = (), info = {}, kwargs = {}".format(root, info, userId))
    msg = {'user_id': userId, 'node_list': nodeList}
    print(msg)
    res = RegiManageNode(
        userId='test1',
        nodeOkCnt=1,
        nodeOkList=['uuid12', 'uuid13']
    )
    # apimanager_client.test(msg)
    # res = {'test':'aaaa'}
    # node = NodeField(
    #     id='1',
    #     capability = 'Leader',
    #     capabilitycode = 'NL',
    #     nodealias = 'Test Leader Node',
    #     nodeuuid = 'uuid-01-02'
    # )

    return res

def resolve_getmanagenode(root, info, userId):
    msg = {'user_id':userId}
    res = GetManageNode(
        userId='test1',
        nodeList=['uuid12','uuid13']
    )
    return res

