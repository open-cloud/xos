""" fake_stub.py

    Implements a simple fake grpc stub to use for unit testing.
"""

import functools

ContentTypeIdCounter = 0;
ContentTypeMap = {}

class FakeObj(object):
    def __init__(self, fields=[], **kwargs):
        super(FakeObj, self).__setattr__("is_set", {})
        super(FakeObj, self).__setattr__("fields", [])

        for f in fields:
            name = f["name"]
            self.fields.append(name)
            setattr(self, name, f["default"])

        super(FakeObj, self).__setattr__("is_set", {})
        for (k,v) in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        lines = []
        for k in self.fields:
            if self.is_set.get(k, False):
                lines.append('%s: "%s"' % (k, getattr(self, k)))
        if lines:
            return "\n".join(lines) + "\n"
        else:
            return ""

    def __setattr__(self, name, value):
        self.is_set[name] = True
        super(FakeObj, self).__setattr__(name, value)

class FakeExtensionManager(object):
    def __init__(self, obj, extensions):
        self.obj = obj
        self.extensions = extensions

    def _FindExtensionByName(self, name):
        return name

    def __getitem__(self, name, default=None):
        if name in self.extensions:
            return self.extensions[name]
        return default

class FakeFieldOption(object):
    def __init__(self, modelName=None):
        self.modelName = modelName

class FakeField(object):
    def __init__(self, field):
        extensions = {}

        fk_model = field.get("fk_model", None)
        if fk_model:
            extensions["xos.foreignKey"] = FakeFieldOption(modelName=fk_model)

        fk_reverse = field.get("fk_reverse", None)
        if fk_reverse:
            extensions["xos.reverseForeignKey"] = FakeFieldOption(modelName=fk_reverse)

        self.Extensions = FakeExtensionManager(self, extensions)

    def GetOptions(self):
        return self

class FakeDescriptor(object):
    def __init__(self, objName):
        global ContentTypeIdCounter
        global ContentTypeMap
        self.objName = objName
        if objName in ContentTypeMap:
            ct = ContentTypeMap[objName]
        else:
            ct = ContentTypeIdCounter
            ContentTypeIdCount = ContentTypeIdCounter + 1
            ContentTypeMap[objName] = ct
        self.Extensions = FakeExtensionManager(self, {"xos.contentTypeId": ct})

    def GetOptions(self):
        return self

    @property
    def fields_by_name(self):
        cls = globals()[self.objName]
        fbn = {}
        for field in cls.FIELDS:
            fake_field = FakeField(field)
            fbn[ field["name"] ] = fake_field

        return fbn

class Slice(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "site_id", "default": 0, "fk_model": "Site"} )

    def __init__(self, **kwargs):
        return super(Slice, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Slice")

class Site(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "slice_ids", "default": 0, "fk_reverse": "Slice"} )

    def __init__(self, **kwargs):
        return super(Site, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Site")

class FakeStub(object):
    def __init__(self):
        self.objs = {}
        for name in ["Slice", "Site"]:
            setattr(self, "Get%s" % name, functools.partial(self.get, name))
            setattr(self, "List%s" % name, functools.partial(self.list, name))
            setattr(self, "Create%s" % name, functools.partial(self.create, name))
            setattr(self, "Delete%s" % name, functools.partial(self.delete, name))
            setattr(self, "Update%s" % name, functools.partial(self.update, name))


    def make_key(self, name, id):
        return "%s:%d" % (name, id.id)

    def get(self, classname, id):
        obj = self.objs.get(self.make_key(classname, id), None)
        return obj

    def list(self, classname, empty):
        items = None
        for (k,v) in self.objs.items():
            (this_classname, id) = k.split(":")
            if this_classname == classname:
                    items.append(v)
        return items

    def create(self, classname, obj):
        k = self.make_key(classname, FakeObj(id=obj.id))
        self.objs[k] = obj

    def update(self, classname, obj):
        # TODO: partial update support?
        k = self.make_key(classname, FakeObj(id=obj.id))
        self.objs[k] = obj

    def delete(self, classname, id):
        k = self.make_key(classname, id)
        del self.objs[k]

class FakeSymDb(object):
    def __init__(self):
        self._classes = {}
        for name in ["Slice", "Site"]:
            self._classes["xos.%s" % name] = globals()[name]



