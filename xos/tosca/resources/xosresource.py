class XOSResource(object):
    xos_base_class = "XOSResource"
    provides = None

    def __init__(self, user, nodetemplate):
        self.dirty = False
        self.user = user
        self.nodetemplate = nodetemplate
        self.process_nodetemplate()

    def get_requirements(self, relationship_name, throw_exception=False):
        """ helper to search the list of requirements for a particular relationship
            type.
        """

        results = []
        for reqs in self.nodetemplate.requirements:
            for (k,v) in reqs.items():
                if (v["relationship"] == relationship_name):
                    results.append(v["node"])

        if (not results) and throw_exception:
            raise Exception("Failed to find requirement in %s using relationship %s" % (self.nodetemplate.name, relationship_name))

        return results

    def get_requirement(self, relationship_name, throw_exception=False):
        reqs = self.get_requirements(relationship_name, throw_exception)
        if not reqs:
            return None
        return reqs[0]

    def get_xos_object(self, cls, **kwargs):
        objs = cls.objects.filter(**kwargs)
        if not objs:
            raise Exception("Failed to find %s filtered by %s" % (cls.__name__, str(kwargs)))
        return objs[0]

    def process_nodetemplate(self):
        pass

    def info(self, s):
        print s

