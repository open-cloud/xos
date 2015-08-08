import pdb

class XOSResource(object):
    xos_base_class = "XOSResource"
    xos_model = None
    provides = None

    def __init__(self, user, nodetemplate, engine):
        self.dirty = False
        self.user = user
        self.nodetemplate = nodetemplate
        self.engine = engine

    def get_all_required_node_names(self):
        results = []
        for reqs in self.nodetemplate.requirements:
            for (k,v) in reqs.items():
                results.append(v["node"])
        return results

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

    def get_scalable(self):
        scalable = self.nodetemplate.get_capabilities().get("scalable", None)
        if scalable:
            return {"min_instances": scalable.get_property_value("min_instances"),
                    "max_instances": scalable.get_property_value("max_instances"),
                    "default_instances": scalable.get_property_value("default_instances")}
        else:
            return {}

    def get_property(self, name):
        return self.nodetemplate.get_property_value(name)

    def get_xos_object(self, cls, **kwargs):
        objs = cls.objects.filter(**kwargs)
        if not objs:
            raise Exception("Failed to find %s filtered by %s" % (cls.__name__, str(kwargs)))
        return objs[0]

    def get_existing_objs(self):
        return self.xos_model.objects.filter(name = self.nodetemplate.name)

    def get_xos_args(self):
        return {}

    def create_or_update(self):
        existing_objs = self.get_existing_objs()
        if existing_objs:
            self.info("%s %s already exists" % (self.xos_model.__name__, self.nodetemplate.name))
            self.update(existing_objs[0])
        else:
            self.create()

    def create(self):
        raise Exception("abstract method -- must override")

    def update(self, obj):
        pass

    def delete(self, obj):
        obj.delete(purge=True)   # XXX TODO: turn off purge before production

    def info(self, s):
        print s

