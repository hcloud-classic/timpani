import dmidecode
import socket
import fcntl
import os
import struct
import platform
import netifaces
import timpani_system.constants

SIOCGIFADDR=0x8915
SIOCGIFHWADDR=0x8927
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

    def get_mac_address(self, ifname):
        mac_address = None
        if platform.system() == "FreeBSD":
            address = netifaces.ifaddresses(ifname)[netifaces.AF_LINK]
            mac_address = address[0]['addr']
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            mac = fcntl.ioctl(s.fileno(),
                          SIOCGIFHWADDR,
                          struct.pack('256s', bytes(ifname[:15], 'utf-8'))
                          )
            print('mac : {}'.format(mac))
            mac_address =  ':'.join(['%02x' % x for x in mac[18:24]])
        return mac_address

    def get_pid(self):
        return os.getpid()

    def setConfig(self):
        amqp_config_value = "{}".format(self.config[timpani_system.constants.RABBITMQ_KEY][timpani_system.constants.AMQP_CONFIG_KEY])
        timpani_system.constants.PLATFORM_TYPE = platform.system()
        timpani_system.constants.AMQP_CONFIG = {}
        timpani_system.constants.AMQP_CONFIG['AMQP_URI'] = amqp_config_value
        timpani_system.constants.NODE_UUID = self.get_system_uuid()
        timpani_system.constants.SERVICE_IPV4ADDR = self.get_ip_address(self.config[timpani_system.constants.SECTION_KEY][timpani_system.constants.IF_NAME_KEY])
        timpani_system.constants.SERVICE_MACADDR = self.get_mac_address(
            self.config[timpani_system.constants.SECTION_KEY][timpani_system.constants.IF_NAME_KEY])
        timpani_system.constants.CAPABILITY = self.config[timpani_system.constants.SECTION_KEY][timpani_system.constants.CAPABILITY_KEY]
        timpani_system.constants.SERVICE_PID = self.get_pid()
