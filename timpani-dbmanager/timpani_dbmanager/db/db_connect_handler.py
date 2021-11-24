from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .models.base import Base
from ..configuration.configuration_file_reader import ConfigrationFileReader

from . import models

GENERNEL = "GENERAL"
SQL_CONNECTION_STRING = "SQL_CONNECTION_STRING"

class DBConnectHandler:

    engine = None

    def __init__(self):
        session = sessionmaker(bind=DBConnectHandler.engine, autocommit=True, autoflush=True)
        session.configure(bind=DBConnectHandler.engine)
        self.trans = sessionmaker(bind=DBConnectHandler.engine)
        self.session = scoped_session(session)
        # autocommit_session = session()
        # self.session = self.trans(bind=autocommit_session)


    @staticmethod
    def initalize_db_connection_handler():
        try:
            config_data, _ = ConfigrationFileReader().read_file()
            DBConnectHandler._connection_string = config_data[GENERNEL][SQL_CONNECTION_STRING]
            DBConnectHandler.engine = create_engine(DBConnectHandler._connection_string, echo=False)
            print("SQL_CONNECTION_STRING : {}".format(DBConnectHandler._connection_string))
            Base.metadata.create_all(DBConnectHandler.engine)
        except KeyError:
            message = "Unable to read %s flag from section %s"%(SQL_CONNECTION_STRING,GENERNEL)
            print("ERROR : {}".format(message))
            exit(1)

