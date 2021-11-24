import os
from os.path import expanduser

WEB_LISTEN_ADDRESS = "127.0.0.1"
WEB_LISTEN_PORT = "80"


AMQP_CONFIG = {'AMQP_URI':"amqp://teratec:teratec@172.32.100.254:5672"}

INTERNAL_TOKEN_LIST = []

class Constants:

    DIR_HOME = expanduser("/etc/timpani/")
    CONFIGURATION_FILE = os.path.join(*(DIR_HOME, "timpani.ini"))
