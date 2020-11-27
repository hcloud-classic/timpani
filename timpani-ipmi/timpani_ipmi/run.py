import re
from timpani_ipmi.ipmi import IPMIManager

def getIPMIsystem_uuid(data):
    res = IPMIManager.get_ipmi_system_uuid(addr=data.get('ipv4addr'), user=data.get('user'), password=data.get('password'))
    print(res)


if __name__ == "__main__":
    data = {'user': 'root', 'password': '123123', 'ipv4addr': '9.9.9.8', 'ipv4port': None}
    getIPMIsystem_uuid(data)


