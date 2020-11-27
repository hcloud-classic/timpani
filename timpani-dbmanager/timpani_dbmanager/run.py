from .db import dao
from .db.db_connect_handler import DBConnectHandler
from .configuration.configuration_file_reader import ConfigrationFileReader

def init_db():
    ipmi_id = dao.ipmi_dao.IpmiDAO.register_ipmi_connection_info("192.168.10.2","632","test","test",0)
    print("ipmi_id : {}".format(ipmi_id))
    #(node_id, node_detail_id) = dao.node_dao.NodeDetailDAO.resigster_node_detail(ipmi_id,"Leader","TEST LEADER Node")
    return node_id# node_detail_id

def main():
    ConfigrationFileReader()
    DBConnectHandler.initalize_db_connection_handler()
    init_db()
    #node_id, node_detail = init_db()
    #result = dao.node_dao.NodeDAO.get_node_information(node_id,None)
    #node_detail_obj = dao.node_dao.NodeDetailDAO.get_node_detail(node_detail)
    #datas = [dict(id=q.id, node=q.node) for q in node_detail_obj]
    #print("RESULT : {}".format(result[0].__dict__))
    #print("RESULT : {}".format(datas))

if __name__=="__main__":
    main()