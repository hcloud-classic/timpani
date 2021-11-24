import configparser
import re

from collections import defaultdict
from ..constants import Constants

class ConfigrationFileReader:
    def __init__(self, filename=Constants.CONFIGURATION_FILE):
        print("CONFIG FILE : {}".format(filename))
        self.filename = filename

    def cleanText(self,readData):
        text = re.sub('[%]','percent',readData)
        return text


    def read_file(self):
        configuration = {}
        db_configuration = {}
        parser = configparser.ConfigParser(inline_comment_prefixes=';')
        # parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read([self.filename], encoding='utf-8')

        for section in parser.sections():
            print("Sesstion : %s " % section)
            configuration[section] = {}
            db_configuration[section] = {}
            for parameter_name, parameter_value in parser.items(section):
                print("option : %s " % parameter_name)
                print("option_value : %s" % parameter_value)
                parameter_name_lower = parameter_name.lower()
                configuration[section][parameter_name] = parameter_value
                db_configuration[section][parameter_name_lower] = parameter_value
        return configuration, db_configuration

# if __name__=='__main__':
#     config = ConfigrationFileReader("test.ini")
#     config_read = config.read_file()
#     print(config_read)
