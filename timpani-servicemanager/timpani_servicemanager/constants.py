import os
from os.path import expanduser

class Constants:
    DIR_HOME = expanduser("/home/timpani/config")
    CONFIGURATION_FILE = os.path.join(*(DIR_HOME, "timpani-servicemanager.ini"))

RABBITMQ_KEY = "RABBITMQ"
AMQP_CONFIG_KEY = "AMQP_URI"
SECTION_KEY = "SERVICEMANAGER"
IF_NAME_KEY = "IF_NAME"
CAPABILITY_KEY = "CAPABILITY"
AMQP_CONFIG = {'AMQP_URI':"amqp://localhost:5672"}