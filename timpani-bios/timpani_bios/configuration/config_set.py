import dmidecode
import socket
import fcntl
import struct
import timpani_bios.constants

class ConfigSetting(object):

    def __init__(self, config):
        self.config = config

    def get_system_uuid(self):
        dmi = dmidecode.DMIDecode()
        return dmi.get("System")[0].get("UUID").replace('-','')

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                            0x8915, # SIOCGIFADDR
                                            struct.pack('256s', bytes(ifname[:15], 'utf-8'))
                                            )[20:24])

    def setConfig(self):
        amqp_config_value = "{}".format(self.config[timpani_bios.constants.RABBITMQ_KEY][timpani_bios.constants.AMQP_CONFIG_KEY])
        timpani_bios.constants.AMQP_CONFIG = {}
        timpani_bios.constants.AMQP_CONFIG['AMQP_URI'] = amqp_config_value
        print(timpani_bios.constants.AMQP_CONFIG)
        timpani_bios.constants.NODE_UUID = self.get_system_uuid()
        timpani_bios.constants.SERVICE_IPV4ADDR = self.get_ip_address(self.config[timpani_bios.constants.SECTION_KEY][timpani_bios.constants.IF_NAME_KEY])
        timpani_bios.constants.CAPABILITY = self.config[timpani_bios.constants.SECTION_KEY][timpani_bios.constants.CAPABILITY_KEY]
        timpani_bios.constants.DEFAULT_BIOS_SYSCFG = self.config[timpani_bios.constants.SECTION_KEY][timpani_bios.constants.DEFAULT_BIOS_SYSCFG_KEY]
        print(timpani_bios.constants.NODE_UUID)
        print(timpani_bios.constants.SERVICE_IPV4ADDR)
        print(timpani_bios.constants.CAPABILITY)
        print(timpani_bios.constants.DEFAULT_BIOS_SYSCFG)
