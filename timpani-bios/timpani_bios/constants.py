import os
from os.path import expanduser

class Constants:

    DIR_HOME = expanduser("/etc/timpani")
    CONFIGURATION_FILE = os.path.join(*(DIR_HOME, "timpani.ini"))

RABBITMQ_KEY = "RABBITMQ"
AMQP_CONFIG_KEY = "AMQP_URI"
SECTION_KEY = "BIOS"
IF_NAME_KEY = "IF_NAME"
CAPABILITY_KEY = "CAPABILITY"
DEFAULT_BIOS_SYSCFG_KEY = "DEFAULT_SYSCFG_PATH"
DEFAULT_BIOS_SYSCFG = "getini_syscfg.INI"
AMQP_CONFIG = {'AMQP_URI':"amqp://localhost:5672"}

AGENT_ID = None
NODE_UUID = None
SERVICE_IPV4ADDR = None
CAPABILITY = None

# DBMANAGER API DEFIND
MTHOD_SET_BIOS_CONFIG = "set_bios_config"

BIOSCONFIGFILE = 'getini_syscfg.INI'
REDFISH_BIOSCONFIGFILE = 'syscfg.INI'