import configparser
import re

from collections import defaultdict
from ..constants import Constants, AMQP_CONFIG

class ConfigrationFileReader:
    def __init__(self, filename=Constants.CONFIGURATION_FILE):
        print("CONFIG FILE : {}".format(filename))
        self.filename = filename

    def cleanText(self,readData):
        text = re.sub('[%]','percent',readData)
        return text


    def read_file(self):
        configuration = defaultdict(dict)

        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read([self.filename], encoding='utf-8')

        for section in parser.sections():
            print("Section : %s " % section)
            for parameter_name, parameter_value in parser.items(section):
                print("option : %s " % parameter_name)
                print("option_value : %s" % parameter_value)

                configuration[section][parameter_name] = parameter_value

        return configuration


