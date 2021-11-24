import os
import logging
import dmidecode
import platform
import socket
import fcntl
import struct
import netifaces

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
stream_hander.setLevel(level=logging.INFO)
logger.addHandler(stream_hander)

class Systemutil(object):

    SIOCGIFADDR = 0x8915
    SIOCGIFHWADDR = 0x8927
    if platform.system() == 'FreeBSD':
        SIOCGIFADDR = 0xc0206921

    def dirExistCheckAndCreate(self, dir):
        try:
            if not os.path.isdir(dir):
                logger.info("create dir : {}".format(dir))
                os.makedirs(dir, mode=0o755)
        except Exception as e:
            logger.info("SYSTEMUTIL EXCEPTION : {}".format(e))
            return False

        return True

    def dirExistCheckAndDelete(self, dir):
        try:
            if not os.path.isdir(dir):
                os.removedirs(dir)
        except Exception:
            return False

        return True

    def getSystemUuid(self):
        dmi = dmidecode.DMIDecode()
        # return dmi.get("System")[0].get("UUID").replace('-','')
        return dmi.get("System")[0].get("UUID")

    def getIpAddress(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                            self.SIOCGIFADDR,
                                            struct.pack('256s', bytes(ifname[:15], 'utf-8'))
                                            )[20:24])

    def getMacAddress(self, ifname):
        mac_address = None
        if platform.system() == "FreeBSD":
            address = netifaces.ifaddresses(ifname)[netifaces.AF_LINK]
            mac_address = address[0]['addr']
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            mac = fcntl.ioctl(s.fileno(),
                          self.SIOCGIFHWADDR,
                          struct.pack('256s', bytes(ifname[:15], 'utf-8'))
                          )
            # print('mac : {}'.format(mac))
            mac_address = ':'.join(['%02x' % x for x in mac[18:24]])
        return mac_address

    def getPid(self):
        return os.getpid()
