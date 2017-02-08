"""
Django-like ORM layer for gRPC

Usage:
    api = ORMStub(stub)

    api.Slices.all() ... list all slices

    someSlice = api.Slices.get(id=1) ... get slice #1

    someSlice.site ... automatically resolves site_id into a site object
    someSlice.instances ... automatically resolves instances_ids into instance objects
    someSlice.save() ... saves the slice object
"""

"""
import grpc_client, orm
c=grpc_client.SecureClient("xos-core.cord.lab", username="padmin@vicci.org", password="letmein")
u=c.xos_orm.User.objects.get(id=1)
"""

import functools
from google.protobuf.empty_pb2 import Empty
from protos.common_pb2 import ID
from protos.xosoptions_pb2 import foreignKey, reverseForeignKey

from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()

class ORMWrapper(object):
    """ Wraps a protobuf object to provide ORM features """

    def __init__(self, wrapped_class, stub, is_new=False):
        super(ORMWrapper, self).__setattr__("_wrapped_class", wrapped_class)
        super(ORMWrapper, self).__setattr__("stub", stub)
        super(ORMWrapper, self).__setattr__("cache", {})
        super(ORMWrapper, self).__setattr__("reverse_cache", {})
        super(ORMWrapper, self).__setattr__("is_new", is_new)
        fkmap=self.gen_fkmap()
        super(ORMWrapper, self).__setattr__("_fkmap", fkmap)
        reverse_fkmap=self.gen_reverse_fkmap()
        super(ORMWrapper, self).__setattr__("_reverse_fkmap", reverse_fkmap)

    def gen_fkmap(self):
        fkmap = {}

        for (name, field) in self._wrapped_class.DESCRIPTOR.fields_by_name.items():
           if name.endswith("_id"):
               fk = field.GetOptions().Extensions[foreignKey]
               if fk:
                   fkmap[name[:-3]] = {"src_fieldName": name, "modelName": fk.modelName}

        return fkmap

    def gen_reverse_fkmap(self):
        reverse_fkmap = {}

        for (name, field) in self._wrapped_class.DESCRIPTOR.fields_by_name.items():
           if name.endswith("_ids"):
               fk = field.GetOptions().Extensions[reverseForeignKey]
               if fk:
                   reverse_fkmap[name[:-4]] = {"src_fieldName": name, "modelName": fk.modelName}

        return reverse_fkmap

    def fk_resolve(self, name):
        if name in self.cache:
            return ORMWrapper(self.cache[name], self.stub)

        fk_entry = self._fkmap[name]
        get_method = getattr(self.stub, "Get%s" % fk_entry["modelName"])
        id=ID(id=getattr(self, fk_entry["src_fieldName"]))
        dest_model = get_method(id)

        self.cache[name] = dest_model

        return ORMWrapper(dest_model, self.stub)

    def reverse_fk_resolve(self, name):
        if name not in self.reverse_cache:
            fk_entry = self._reverse_fkmap[name]
            self.cache[name] = ORMLocalObjectManager(self.stub, fk_entry["modelName"], getattr(self, fk_entry["src_fieldName"]))

        return self.cache[name]

    def __getattr__(self, name, *args, **kwargs):
        # note: getattr is only called for attributes that do not exist in
        #       self.__dict__

        if name in self._fkmap.keys():
            return self.fk_resolve(name)

        if name in self._reverse_fkmap.keys():
            return self.reverse_fk_resolve(name)

        return getattr(self._wrapped_class, name, *args, **kwargs)

    def __setattr__(self, name, value):
        if name in self.__dict__:
            super(ORMWrapper,self).__setattr__(name, value)
        else:
            setattr(self._wrapped_class, name, value)

    def __repr__(self):
        return self._wrapped_class.__repr__()

    def save(self):
        if self.is_new:
           create_method = getattr(self.stub,"Create%s" % self._wrapped_class.__class__.__name__)
           new_class = create_method(self._wrapped_class)
           self._wrapped_class = new_class
           self.is_new = False
        else:
           update_method = getattr(self.stub,"Update%s" % self._wrapped_class.__class__.__name__)
           update_method(self._wrapped_class)

    def delete(self):
        delete_method = getattr(self.stub,"Delete%s" % self._wrapped_class.__class__.__name__)
        id = ID(id=self._wrapped_class.id)
        delete_method(id)

class ORMLocalObjectManager(object):
    """ Manages a local list of objects """

    def __init__(self, stub, modelName, idList):
        self._stub = stub
        self._modelName = modelName
        self._idList = idList
        self._cache = None

    def resolve_queryset(self):
        if self._cache is not None:
            return self._cache

        models = []
        get_method = getattr(self._stub, "Get%s" % self._modelName)
        for id in self._idList:
            models.append(get_method(ID(id=id)))

        self._cache = models

        return models

    def all(self):
        models = self.resolve_queryset()
        return [ORMWrapper(x,self._stub) for x in models]

class ORMObjectManager(object):
    """ Manages a remote list of objects """

    def __init__(self, stub, modelName, packageName):
        self._stub = stub
        self._modelName = modelName
        self._packageName = packageName

    def wrap_single(self, obj):
        return ORMWrapper(obj, self._stub)

    def wrap_list(self, obj):
        result=[]
        for item in obj.items:
            result.append(ORMWrapper(item, self._stub))
        return result

    def all(self):
        list_method = getattr(self._stub, "List%s" % self._modelName)
        return self.wrap_list(list_method(Empty()))

    def get(self, id):
        get_method = getattr(self._stub, "Get%s" % self._modelName)
        return self.wrap_single(get_method(ID(id=id)))

    def new(self, **kwargs):
        full_model_name = "%s.%s" % (self._packageName, self._modelName)
        cls = _sym_db._classes[full_model_name]
        return ORMWrapper(cls(), self._stub, is_new=True)

class ORMModelClass(object):
    def __init__(self, stub, model_name, package_name):
        self.objects = ORMObjectManager(stub, model_name, package_name)

class ORMStub(object):
    def __init__(self, stub, package_name):
        for name in dir(stub):
           if name.startswith("Get"):
               model_name = name[3:]
               setattr(self,model_name, ORMModelClass(stub, model_name, package_name))

#def wrap_get(*args, **kwargs):
#    stub=kwargs.pop("stub")
#    getmethod=kwargs.pop("getmethod")
#    result = getmethod(*args, **kwargs)
#    return ORMWrapper(result)
#
#def wrap_stub(stub):
#    for name in dir(stub):
#        if name.startswith("Get"):
#            setattr(stub, name, functools.partial(wrap_get, stub=stub, getmethod=getattr(stub,name)))

