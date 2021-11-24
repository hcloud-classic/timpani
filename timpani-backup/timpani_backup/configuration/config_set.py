import dmidecode
import socket
import fcntl
import struct
import platform
import timpani_backup.constants

SIOCGIFADDR=0x8915
if platform.system() == 'FreeBSD':
    SIOCGIFADDR=0xc0206921

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
                                            SIOCGIFADDR,
                                            struct.pack('256s', bytes(ifname[:15], 'utf-8'))
                                            )[20:24])

    def setConfig(self):
        amqp_config_value = "{}".format(self.config[timpani_backup.constants.RABBITMQ_KEY][timpani_backup.constants.AMQP_CONFIG_KEY])
        timpani_backup.constants.PLATFORM_TYPE = platform.system()
        timpani_backup.constants.AMQP_CONFIG = {}
        timpani_backup.constants.AMQP_CONFIG['AMQP_URI'] = amqp_config_value
        print(timpani_backup.constants.AMQP_CONFIG)
        timpani_backup.constants.NODE_UUID = self.get_system_uuid()
        timpani_backup.constants.SERVICE_IPV4ADDR = self.get_ip_address(self.config[timpani_backup.constants.SECTION_KEY][timpani_backup.constants.IF_NAME_KEY])
        timpani_backup.constants.CAPABILITY = self.config[timpani_backup.constants.SECTION_KEY][timpani_backup.constants.CAPABILITY_KEY]
        print(timpani_backup.constants.NODE_UUID)
        print(timpani_backup.constants.SERVICE_IPV4ADDR)
        print(timpani_backup.constants.CAPABILITY)
        print(timpani_backup.constants.PLATFORM_TYPE)
