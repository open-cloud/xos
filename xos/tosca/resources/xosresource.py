class XOSResource(object):
    xos_base_class = "XOSResource"
    provides = None

    def __init__(self, user, nodetemplate):
        self.user = user
        self.nodetemplate = nodetemplate
        self.process_nodetemplate()

    def process_nodetemplate(self):
        pass

    def save(self):
        pass

