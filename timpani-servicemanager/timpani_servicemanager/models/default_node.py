class DefaultNode(object):
    nodeuuid = None
    capability = None
    alias = None

    def __init__(self, nodeuuid):
        self.nodeuuid = nodeuuid
        self.capability = "Leader"
        self.alias = "Leader"


