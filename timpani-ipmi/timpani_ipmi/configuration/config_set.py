import dmidecode
import socket
import fcntl
import struct
import timpani_ipmi.constants

class ConfigSetting(object):

    def __init__(self, config):
        self.config = config

    def get_system_uuid(self):
        dmi = dmidecode.DMIDecode()
        # return dmi.get("System")[0].get("UUID").replace('-','')
        return dmi.get("System")[0].get("UUID")

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                            0x8915, # SIOCGIFADDR
                                            struct.pack('256s', bytes(ifname[:15], 'utf-8'))
                                            )[20:24])

    def setConfig(self):
        amqp_config_value = "{}".format(self.config[timpani_ipmi.constants.RABBITMQ_KEY][timpani_ipmi.constants.AMQP_CONFIG_KEY])
        timpani_ipmi.constants.AMQP_CONFIG = {}
        timpani_ipmi.constants.AMQP_CONFIG['AMQP_URI'] = amqp_config_value
        print(timpani_ipmi.constants.AMQP_CONFIG)
        timpani_ipmi.constants.NODE_UUID = self.get_system_uuid()
        timpani_ipmi.constants.SERVICE_IPV4ADDR = self.get_ip_address(self.config[timpani_ipmi.constants.SECTION_KEY][timpani_ipmi.constants.IF_NAME_KEY])
        timpani_ipmi.constants.CAPABILITY = self.config[timpani_ipmi.constants.SECTION_KEY][timpani_ipmi.constants.CAPABILITY_KEY]
        print(timpani_ipmi.constants.NODE_UUID)
        print(timpani_ipmi.constants.SERVICE_IPV4ADDR)
        print(timpani_ipmi.constants.CAPABILITY)
