from .db import dao
from .db.db_connect_handler import DBConnectHandler
from .configuration.configuration_file_reader import ConfigrationFileReader
import sys
import time
from .api.app import AppAPI
from .api.sync import SyncAPI
from nameko.containers import ServiceContainer
from .service import DbmanagerService


def sync_test():
    sync_api = SyncAPI()
    test_uuid = 'masternodeuuid'
    data = {'uuid':test_uuid}
    res = sync_api.getNodetype(data)
    print("SYNC FIND NODETYPE : {}".format(res))

def main():
    app_api = AppAPI()
    config = ConfigrationFileReader()
    config_data, db_config_data = config.read_file()
    print("CONFIG DATA : \n{}".format(db_config_data))
    try:
        # container = ServiceContainer(DbmanagerService, amqp_config)
        # container.start()
        print("Container started")
        app_api.setconfig(db_config_data.get('GENERAL'))
        data = {}
        res = app_api.getconfig(data)
        print("ALL Config DATA : {}".format(res))

        data['get_kind'] = 'MASTER'
        res = app_api.getconfig(data)
        print("MASTER Config DATA : {}".format(res))

        data['get_kind'] = 'STORAGE'
        res = app_api.getconfig(data)
        print("STORAGE Config DATA : {}".format(res))

        data['get_kind'] = 'IPMI'
        res = app_api.getconfig(data)
        print("IPMI Config DATA : {}".format(res))

        data['get_kind'] = 'NFS'
        res = app_api.getconfig(data)
        print("NFS Config DATA : {}".format(res))
        # print("Container started! : Service name [ {} ]".format(DbmanagerService.__name__))

        data = {'nodetype':'STORAGE'}
        res = app_api.getmodulename(data)
        print("get MODULENAME : {}".format(res))
        sync_test()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # Ctrl+C
        print("Input Ctrl+C")
        # container.stop()
        sys.exit()

if __name__=="__main__":
    main()

