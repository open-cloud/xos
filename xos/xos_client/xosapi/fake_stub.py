
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

    def HasField(self, name):
        """ Return True if the field is set in the protobuf. """

        # gRPC throws a valueerror if the field doesn't exist in the schema
        if name not in self.fields:
            raise ValueError("Field %s does not exist in schema" % name)

        # Fields that are always set
        if name in ["leaf_model_name"]:
            return True

        field = self.DESCRIPTOR.fields_by_name[name].field_decl

        # Reverse foreign keys lists are never None, they are an empty list
        if field.get("fk_reverse", None):
            return True

        return self.is_set.get(name, False)

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
    def __init__(self, modelName=None, reverseFieldName=None):
        self.modelName = modelName
        self.reverseFieldName = reverseFieldName

class FakeField(object):
    def __init__(self, field):
        extensions = {}

        self.field_decl = field

        fk_model = field.get("fk_model", None)
        if fk_model:
            reverseFieldName = field.get("fk_reverseFieldName", None)
            extensions["xos.foreignKey"] = FakeFieldOption(modelName=fk_model, reverseFieldName=reverseFieldName)

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
               {"name": "deployment_id", "default": 0, "fk_model": "Deployment"},
               {"name": "class_names", "default": "Controller"}
             )

    def __init__(self, **kwargs):
        return super(Controller, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Controller")

class Deployment(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "class_names", "default": "Deployment"}
             )

    def __init__(self, **kwargs):
        return super(Deployment, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Controller")

class User(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "email", "default": ""},
               {"name": "site_id", "default": 0, "fk_model": "Site"},
               {"name": "class_names", "default": "User"} )

    def __init__(self, **kwargs):
        return super(User, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("User")

class Slice(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "site_id", "default": 0, "fk_model": "Site", "fk_reverseFieldName": "slices"},
               {"name": "service_id", "default": 0, "fk_model": "Service"},
               {"name": "creator_id", "default": 0, "fk_model": "User"},
               {"name": "networks_ids", "default": [], "fk_reverse": "Network"},
               {"name": "network", "default": ""},
               {"name": "leaf_model_name", "default": "Slice"},
               {"name": "class_names", "default": "Slice"} )

    def __init__(self, **kwargs):
        return super(Slice, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Slice")

class Site(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "slices_ids", "default": [], "fk_reverse": "Slice"},
               {"name": "leaf_model_name", "default": "Site"},
               {"name": "class_names", "default": "Site"})

    def __init__(self, **kwargs):
        return super(Site, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Site")

class Service(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "slices_ids", "default": [], "fk_reverse": "Slice"},
               {"name": "leaf_model_name", "default": "Service"},
               {"name": "class_names", "default": "Service"})

    def __init__(self, **kwargs):
        return super(Service, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Service")

class ServiceInstance(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "owher", "default": 0, "fk_model": "Service"},
               {"name": "leaf_model_name", "default": "ServiceInstance"},
               {"name": "class_names", "default": "ServiceInstance"})

    def __init__(self, **kwargs):
        return super(ServiceInstance, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("ServiceInstance")

class ONOSService(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "leaf_model_name", "default": "ONOSService"},
               {"name": "class_names", "default": "ONOSService,Service"})

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
               {"name": "leaf_model_name", "default": "Network"},
               {"name": "class_names", "default": "Network"})

    def __init__(self, **kwargs):
        return super(Network, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Network")

class NetworkTemplate(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "name", "default": ""},
               {"name": "vtn_kind", "default": ""},
               {"name": "leaf_model_name", "default": "NetworkTemplate"},
               {"name": "class_names", "default": "NetworkTemplate"})

    def __init__(self, **kwargs):
        return super(NetworkTemplate, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("NetworkTemplate")

class ControllerNetwork(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "network_id", "default": 0, "fk_model": "Network"},
               {"name": "controller_id", "default": 0, "fk_model": "Controller"},
               {"name": "leaf_model_name", "default": "ControllerNetwork"},
               {"name": "class_names", "default": "ControllerNetwork"})

    def __init__(self, **kwargs):
        return super(ControllerNetwork, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("ControllerNetwork")

class NetworkSlice(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "network_id", "default": 0, "fk_model": "Network"},
               {"name": "slice_id", "default": 0, "fk_model": "Slice"},
               {"name": "leaf_model_name", "default": "NetworkSlice"},
               {"name": "class_names", "default": "NetworkSlice"})

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
               {"name": "leaf_model_name", "default": "Tag"},
               {"name": "class_names", "default": "Tag"})

    def __init__(self, **kwargs):
        return super(Tag, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("Tag")

class TestModel(FakeObj):
    FIELDS = ( {"name": "id", "default": 0},
               {"name": "intfield", "default": 0},
               {"name": "class_names", "default": "TestModel"} )

    def __init__(self, **kwargs):
        return super(TestModel, self).__init__(self.FIELDS, **kwargs)

    DESCRIPTOR = FakeDescriptor("TestModel")


class ID(FakeObj):
    pass

class FakeItemList(object):
    def __init__(self, items):
        self.items = items

class FakeElement(object):
    EQUAL="equal"

    def __init__(self):
        pass

class FakeElements(object):
    def __init__(self):
        self.items = []

    def add(self):
        el=FakeElement()
        self.items.append(el)
        return el

class FakeQuery(object):
    DEFAULT="default"

    def __init__(self):
        self.elements = FakeElements()

class FakeStub(object):
    def __init__(self):
        self.id_counter = 1
        self.objs = {}
        for name in ["Controller", "Deployment", "Slice", "Site", "Tag", "Service", "ServiceInstance", "ONOSService",
                     "User", "Network", "NetworkTemplate", "ControllerNetwork", "NetworkSlice",
                     "TestModel"]:
            setattr(self, "Get%s" % name, functools.partial(self.get, name))
            setattr(self, "List%s" % name, functools.partial(self.list, name))
            setattr(self, "Create%s" % name, functools.partial(self.create, name))
            setattr(self, "Delete%s" % name, functools.partial(self.delete, name))
            setattr(self, "Update%s" % name, functools.partial(self.update, name))
            setattr(self, "Filter%s" % name, functools.partial(self.filter, name))


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

    def filter(self, classname, query, metadata=None):
        items = []
        for (k,v) in self.objs.items():
            (this_classname, id) = k.split(":")
            if this_classname != classname:
                continue
            for q in query.elements.items:
                iValue = getattr(q, "iValue", None)
                if (iValue is not None) and getattr(v,q.name)!=iValue:
                    continue
                sValue = getattr(q, "sValue", None)
                if (sValue is not None) and getattr(v, q.name) != sValue:
                    continue
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

class FakeCommonProtos(object):
    def __init__(self):
        self.ID = ID
        self.Query = FakeQuery

class FakeProtos(object):
    def __init__(self):
        for name in ["Controller", "Deployment", "Slice", "Site", "ID", "Tag", "Service", "ServiceInstance",
                     "ONOSService", "User", "Network", "NetworkTemplate", "ControllerNetwork", "NetworkSlice",
                     "TestModel"]:
            setattr(self, name, globals()[name])
            self.common__pb2 = FakeCommonProtos()

class FakeSymDb(object):
    def __init__(self):
        self._classes = {}
        for name in ["Controller", "Deployment", "Slice", "Site", "ID", "Tag", "Service", "ServiceInstance",
                     "ONOSService", "User", "Network", "NetworkTemplate", "ControllerNetwork", "NetworkSlice",
                     "TestModel"]:
            self._classes["xos.%s" % name] = globals()[name]



