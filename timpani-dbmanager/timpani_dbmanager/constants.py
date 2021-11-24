import os
from os.path import expanduser
class Constants:

    DIR_HOME = expanduser("/etc/timpani")
    CONFIGURATION_FILE = os.path.join(*(DIR_HOME, "timpani.ini"))
