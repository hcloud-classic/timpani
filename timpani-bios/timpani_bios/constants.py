import os
from os.path import expanduser

class Constants:

    DIR_HOME = expanduser("/home/timpani/config")
    CONFIGURATION_FILE = os.path.join(*(DIR_HOME, "timpani-bios.ini"))

RABBITMQ_KEY = "RABBITMQ"
AMQP_CONFIG_KEY = "AMQP_URI"
SECTION_KEY = "BIOS"
IF_NAME_KEY = "IF_NAME"
CAPABILITY_KEY = "CAPABILITY"
DEFAULT_BIOS_SYSCFG_KEY = "DEFAULT_SYSCFG_PATH"
DEFAULT_BIOS_SYSCFG = "test_syscfg.INI"
AMQP_CONFIG = {'AMQP_URI':"amqp://localhost:5672"}

AGENT_ID = None
NODE_UUID = None
SERVICE_IPV4ADDR = None
CAPABILITY = None

# DBMANAGER API DEFIND
MTHOD_SET_BIOS_CONFIG = "set_bios_config"