import os
from os.path import expanduser

class Constants:

    DIR_HOME = expanduser("/etc/timpani/")
    CONFIGURATION_FILE = os.path.join(*(DIR_HOME, "timpani.ini"))

RABBITMQ_KEY = "RABBITMQ"
AMQP_CONFIG_KEY = "AMQP_URI"
SECTION_KEY = "FILEMANAGER"
IF_NAME_KEY = "IF_NAME"
CAPABILITY_KEY = "CAPABILITY"
AMQP_CONFIG = {'AMQP_URI':"amqp://localhost:5672"}

AGENT_ID = None
NODE_UUID = None
SERVICE_IPV4ADDR = None
CAPABILITY = None
BASE_STORAGE_URI = "/home/timpani"