class XOSResource(object):
    xos_base_class = "XOSResource"
    provides = None

    def __init__(self, user, nodetemplate):
        self.dirty = False
        self.user = user
        self.nodetemplate = nodetemplate
        self.process_nodetemplate()

    def get_requirement(self, relationship_name, throw_exception=False):
        """ helper to search the list of requirements for a particular relationship
            type.
        """
        for reqs in self.nodetemplate.requirements:
            for (k,v) in reqs.items():
                if (v["relationship"] == relationship_name):
                    return v["node"]

        if throw_exception:
            raise Exception("Failed to find requirement in %s using relationship %s" % (self.nodetemplate.name, relationship_name))

        return None

    def get_xos_object(self, cls, **kwargs):
        objs = cls.objects.filter(**kwargs)
        if not objs:
            raise Exception("Failed to find %s filtered by %s" % (cls.__name__, str(kwargs)))
        return objs[0]

    def process_nodetemplate(self):
        pass

    def save(self):
        pass

    def save_if_dirty(self):
        if self.dirty:
            self.save()
            self.dirty=False

    def info(self, s):
        print s

