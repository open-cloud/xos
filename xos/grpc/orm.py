"""
Django-like ORM layer for gRPC

Usage:
    api = ORMStub(stub)

    api.Slices.all() ... list all slices

    someSlice = api.Slices.get(id=1) ... get slice #1

    someSlice.site ... automatically resolves site_id into a site object
    someSlice.save() ... saves the slice object
"""

"""
import grpc_client, orm
c=grpc_client.SecureClient("xos-core.cord.lab", username="padmin@vicci.org", password="letmein")
xos_orm=orm.ORMStub(c.stub)
u=xos_orm.User.objects.get(id=1)
"""

import functools
import grpc_client
from google.protobuf.empty_pb2 import Empty
from protos.common_pb2 import ID
from protos.xosoptions_pb2 import foreignKey

class ORMWrapper(object):
    def __init__(self, wrapped_class, stub):
        super(ORMWrapper, self).__setattr__("_wrapped_class", wrapped_class)
        super(ORMWrapper, self).__setattr__("stub", stub)
        super(ORMWrapper, self).__setattr__("cache", {})
        fkmap=self.gen_fkmap()
        super(ORMWrapper, self).__setattr__("_fkmap", fkmap)

    def gen_fkmap(self):
        fkmap = {}

        for (name, field) in self._wrapped_class.DESCRIPTOR.fields_by_name.items():
           if name.endswith("_id"):
               fk = field.GetOptions().Extensions[foreignKey]
               if fk:
                   fkmap[name[:-3]] = {"src_fieldName": name, "modelName": fk.modelName}

        return fkmap

    def fk_resolve(self, name):
        if name in self.cache:
            return ORMWrapper(self.cache[name], self.stub)

        fk_entry = self._fkmap[name]
        get_method = getattr(self.stub, "Get%s" % fk_entry["modelName"])
        id=ID(id=getattr(self, fk_entry["src_fieldName"]))
        dest_model = get_method(id)

        self.cache[name] = dest_model

        return ORMWrapper(dest_model, self.stub)

    def __getattr__(self, name, *args, **kwargs):
        # note: getattr is only called for attributes that do not exist in
        #       self.__dict__

        if name in self._fkmap.keys():
            return self.fk_resolve(name)

        return getattr(self._wrapped_class, name, *args, **kwargs)

    def __setattr__(self, name, value):
        if name in self.__dict__:
            super(ORMWrapper,self).__setattr__(name, value)
        else:
            setattr(self._wrapped_class, name, value)

    def __repr__(self):
        return self._wrapped_class.__repr__()

    def save(self):
        update_method = getattr(self.stub,"Update%s" % self._wrapped_class.__class__.__name__)
        update_method(self._wrapped_class)

    def delete(self):
        delete_method = getattr(self.stub,"Delete%s" % self._wrapped_class.__class__.__name__)
        id = ID(id=self._wrapped_class.id)
        delete_method(id)

class ORMObjectManager(object):
    def __init__(self, stub, modelName):
        self._stub = stub
        self._modelName = modelName

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

class ORMModelClass(object):
    def __init__(self, stub, model_name):
        self.objects = ORMObjectManager(stub, model_name)

class ORMStub(object):
    def __init__(self, stub):
        for name in dir(stub):
           if name.startswith("Get"):
               model_name = name[3:]
               setattr(self,model_name, ORMModelClass(stub, model_name))

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

