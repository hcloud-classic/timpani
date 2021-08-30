class RegisterService:
    node_uuid = None
    capability = None
    ipv4address = None
    ipv4port = None
    macaddress = None
    pid = None

    def __init__(self, node_uuid, capability, ipv4address, macaddress, pid, ipv4port=None):
        self.node_uuid = node_uuid
        self.capability = capability
        self.ipv4address = ipv4address
        self.ipv4port = ipv4port
        self.macaddress = macaddress
        self.pid = pid
