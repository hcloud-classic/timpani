
######################### NAMEKO CLIENT CONNECTION #############################
# NAMEKO_AMQP_URI = {'AMQP_URI':"amqp://teratec:teratec@172.32.100.254:5672"}
NAMEKO_AMQP_URI = {'AMQP_URI':"amqp://teratec:teratec@192.168.221.202:5672"}
######################### NODE SYNC DEFAULT DATA ###############################
#QL_URL = 'http://192.168.10.101:38080/graphql'
QL_URL = 'http://192.168.221.1:38080/graphql'
SYNC_PROC_PARAM_NAME = 'sync_proc'
SYNC_PROC_PRE = 'PRE'
SYNC_PROC_UPDATE = 'UPDATE'
SYNC_PROC_AFTER = 'AFTER'
SYNC_PROC_HIST = 'HIST'
SYNC_PROC = [SYNC_PROC_PRE, SYNC_PROC_UPDATE, SYNC_PROC_AFTER]
SYNC_NAME_NODE = "node_sync"
SYNC_CODE_NODE = "DA20"
SYNC_TYPECODE_NODE = "20"
SYNC_KINDCODE_NODE = "DA"
SYNC_DEFAULT_DELAY = "300"  # 5min = 60*5

