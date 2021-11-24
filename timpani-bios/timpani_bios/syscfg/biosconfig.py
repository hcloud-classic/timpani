import configparser
import re

from collections import defaultdict

class BiosConfig(object):

    def filter_str(self, string):
        pattern = '[\t]'
        s = re.sub(pattern=pattern, repl='', string=string)
        return s.strip(' ')

    def read_syscfg(self, file_path):
        configuration = defaultdict(dict)

        #parser = configparser.ConfigParser(inline_comment_prefixes=';')
        parser = configparser.RawConfigParser()
        parser.optionxform = str
        parser.read([file_path], encoding='utf-8')
        syscfg_data = []
        for section in parser.sections():
            options=[]
            for parameter_name, parameter_value in parser.items(section):
                value = parameter_value.replace(r'\t',r' ',True).split(';')
                avail = []
                if len(value) == 2:
                    available = value[1]
                    if value[1].find("Options") >= 0:
                        if value[1][9:].find(":") >= 0:
                            val = value[1][9:].split(':')
                        elif value[1][9:].find(",") >= 0:
                            val = value[1][9:].split(',')
                        elif value[1][9:].find("or") >= 0:
                            val = value[1][9:].split('or')
                        else:
                            val = []

                        for avail_val in val:
                            key=hex_id=''
                            if avail_val.find("=") >= 0:
                                v = avail_val.split('=')
                                key = self.filter_str(v[0])
                                hex_id = self.filter_str(v[1])
                            else:
                                key = self.filter_str(avail_val)
                                hex_id = 'ff'

                            avail.append({'avail_key':key,'hex_id':hex_id})


                data = {'key':parameter_name,'value':self.filter_str(value[0]), 'available':avail}
                options.append(data)
                configuration[section][parameter_name] = parameter_value
            #print(options)
            syscfg_data.append({'section_key':section,'options':options})

        return syscfg_data

    def getini_read(self, src_path, guid, macaddr):

        parser = configparser.ConfigParser(inline_comment_prefixes=';')
        parser.optionxform = str
        parser.read([src_path], encoding='utf-8')
        syscfg_data = []
        for section in parser.sections():
            for k, v in parser.items(section):
                syscfg_data.append({'guid': guid, 'macaddr': macaddr, 'section': section,
                                    'syscfg_key': k, 'cfg_set_val': v})
        return syscfg_data


