import os
from os.path import expanduser
class Constants:

    DIR_HOME = expanduser(".")
    CONFIGURATION_FILE = os.path.join(*(DIR_HOME,"db_test.ini"))
