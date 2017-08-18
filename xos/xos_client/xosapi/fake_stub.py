
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


""" fake_stub.py

    Implements a simple fake grpc stub to use for unit testing.
"""

import functools

ContentTypeMap = {}

class FakeObj(object):
    BASES=[]

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

    @property
    def self_content_type_id(self):
        return "xos.%s" % self.__class__.__name__.lower()

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
            ct = "xos.%s" % objName.lower()
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

class Controller(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "deployment_id", "default": 0, "fk_model": "Deployment"}
             )

    def __init__(self, **kwargs):
        return super(Controller, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Controller")

class Deployment(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
             )

    def __init__(self, **kwargs):
        return super(Deployment, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Controller")

class User(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "email", "default": ""},
               {"name": "site_id", "default": 0, "fk_model": "Site"}, )

    def __init__(self, **kwargs):
        return super(User, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("User")

class Slice(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "site_id", "default": 0, "fk_model": "Site"},
               {"name": "service_id", "default": 0, "fk_model": "Service"},
               {"name": "creator_id", "default": 0, "fk_model": "User"},
               {"name": "networks_ids", "default": [], "fk_reverse": "Network"},
               {"name": "network", "default": ""},
               {"name": "leaf_model_name", "default": "Slice"} )

    def __init__(self, **kwargs):
        return super(Slice, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Slice")

class Site(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "slice_ids", "default": [], "fk_reverse": "Slice"},
               {"name": "leaf_model_name", "default": "Site"})

    def __init__(self, **kwargs):
        return super(Site, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Site")

class Service(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "slices_ids", "default": [], "fk_reverse": "Slice"},
               {"name": "leaf_model_name", "default": "Service"})

    def __init__(self, **kwargs):
        return super(Service, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Service")

class ONOSService(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "leaf_model_name", "default": "ONOSService"})

    BASES = ["Service"]

    def __init__(self, **kwargs):
        return super(ONOSService, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("ONOSService")

class Network(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "owner_id", "default": 0, "fk_model": "Slice"},
               {"name": "template_id", "default": 0, "fk_model": "NetworkTemplate"},
               {"name": "controllernetworks_ids", "default": [], "fk_reverse": "ControllerNetwork"},
               {"name": "leaf_model_name", "default": "Network"})

    def __init__(self, **kwargs):
        return super(Network, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Network")

class NetworkTemplate(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "vtn_kind", "default": ""},
               {"name": "leaf_model_name", "default": "NetworkTemplate"})

    def __init__(self, **kwargs):
        return super(NetworkTemplate, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("NetworkTemplate")

class ControllerNetwork(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "network_id", "default": 0, "fk_model": "Network"},
               {"name": "controller_id", "default": 0, "fk_model": "Controller"},
               {"name": "leaf_model_name", "default": "ControllerNetwork"})

    def __init__(self, **kwargs):
        return super(ControllerNetwork, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("ControllerNetwork")

class NetworkSlice(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "network_id", "default": 0, "fk_model": "Network"},
               {"name": "slice_id", "default": 0, "fk_model": "Slice"},
               {"name": "leaf_model_name", "default": "ControllerNetwork"})

    def __init__(self, **kwargs):
        return super(NetworkSlice, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("NetworkSlice")

class Tag(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "service_id", "default": None},
               {"name": "name", "default": ""},
               {"name": "value", "default": ""},
               {"name": "content_type", "default": None},
               {"name": "object_id", "default": None},
               {"name": "leaf_model_name", "default": "Tag"})

    def __init__(self, **kwargs):
        return super(Tag, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Tag")

class ID(FakeObj):
    pass

class FakeItemList(object):
    def __init__(self, items):
        self.items = items

class FakeStub(object):
    def __init__(self):
        self.id_counter = 1
        self.objs = {}
        for name in ["Controller", "Deployment", "Slice", "Site", "Tag", "Service", "ONOSService", "User", "Network", "NetworkTemplate", "ControllerNetwork", "NetworkSlice"]:
            setattr(self, "Get%s" % name, functools.partial(self.get, name))
            setattr(self, "List%s" % name, functools.partial(self.list, name))
            setattr(self, "Create%s" % name, functools.partial(self.create, name))
            setattr(self, "Delete%s" % name, functools.partial(self.delete, name))
            setattr(self, "Update%s" % name, functools.partial(self.update, name))


    def make_key(self, name, id):
        return "%s:%d" % (name, id.id)

    def get(self, classname, id, metadata=None):
        obj = self.objs.get(self.make_key(classname, id), None)
        return obj

    def list(self, classname, empty, metadata=None):
        items = []
        for (k,v) in self.objs.items():
            (this_classname, id) = k.split(":")
            if this_classname == classname:
                    items.append(v)
        return FakeItemList(items)

    def create(self, classname, obj, metadata=None):
        obj.id = self.id_counter
        self.id_counter = self.id_counter + 1
        k = self.make_key(classname, FakeObj(id=obj.id))
        self.objs[k] = obj

        for base_classname in obj.BASES:
            base_class = globals()[base_classname]
            base_obj = base_class(id=obj.id, leaf_model_name = classname)
            k = self.make_key(base_classname, base_obj)
            self.objs[k] = base_obj

        return obj

    def update(self, classname, obj, metadata=None):
        # TODO: partial update support?
        k = self.make_key(classname, FakeObj(id=obj.id))
        self.objs[k] = obj
        return obj

    def delete(self, classname, id, metadata=None):
        k = self.make_key(classname, id)
        del self.objs[k]

class FakeSymDb(object):
    def __init__(self):
        self._classes = {}
        for name in ["Controller", "Deployment", "Slice", "Site", "ID", "Tag", "Service", "ONOSService", "User", "Network", "NetworkTemplate", "ControllerNetwork", "NetworkSlice"]:
            self._classes["xos.%s" % name] = globals()[name]



