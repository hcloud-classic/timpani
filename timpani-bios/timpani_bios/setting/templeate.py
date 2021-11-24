import configparser
import re

from collections import defaultdict

class Template(object):

    def read(self, path):
        parser = configparser.ConfigParser(inline_comment_prefixes=';')
        parser.optionxform = str
        parser.read([path], encoding='utf-8')
        templeate_data = []
        for section in parser.sections():
            for k, v in parser.items(section):
                save_data = {'name': section, 'redfish_key': k, 'redfish_val': v}
                templeate_data.append(save_data)
        return templeate_data

    def read_definevalue(self, path):
        parser = configparser.ConfigParser(inline_comment_prefixes=';')
        parser.optionxform = str
        parser.read([path], encoding='utf-8')
        redfish_val_define = []
        for section in parser.sections():
            for k, v in parser.items(section):
                save_data = {'redfish_key':section, 'cfg_set_val': k, 'redfish_val': v}
                redfish_val_define.append(save_data)
        return redfish_val_define

    def read_match(self, path):
        parser = configparser.ConfigParser(inline_comment_prefixes=';')
        parser.optionxform = str
        parser.read([path], encoding='utf-8')
        match_list = []
        print("match path : {}".format(path))
        for section in parser.sections():
            print("section : {}".format(section))
            for k, v in parser.items(section):
                save_data = {'match_kind': section, 'redfish_key': k, 'syscfg_key': v}
                match_list.append(save_data)
        return match_list

    def template_setting_data(self, templatelist, definevallist):

        for templeate_data in templatelist:
            data_redfish_key = templeate_data.get('redfish_key')
            data_redfish_val = templeate_data.get('redfish_val')
            for value_data in definevallist:
                redfish_key = value_data.get('redfish_key')
                redfish_val = value_data.get('redfish_val')
                cfg_set_val = value_data.get('cfg_set_val')
                if redfish_key.__eq__(data_redfish_key) and redfish_val == data_redfish_val:
                    templeate_data['cfg_set_val'] = cfg_set_val
        return templatelist