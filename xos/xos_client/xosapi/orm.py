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
import grpc
from google.protobuf.empty_pb2 import Empty
import time

from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()

convenience_wrappers = {}

class ORMWrapper(object):
    """ Wraps a protobuf object to provide ORM features """

    def __init__(self, wrapped_class, stub, is_new=False):
        super(ORMWrapper, self).__setattr__("_wrapped_class", wrapped_class)
        super(ORMWrapper, self).__setattr__("stub", stub)
        super(ORMWrapper, self).__setattr__("cache", {})
        super(ORMWrapper, self).__setattr__("reverse_cache", {})
        super(ORMWrapper, self).__setattr__("poisoned", {})
        super(ORMWrapper, self).__setattr__("is_new", is_new)
        fkmap=self.gen_fkmap()
        super(ORMWrapper, self).__setattr__("_fkmap", fkmap)
        reverse_fkmap=self.gen_reverse_fkmap()
        super(ORMWrapper, self).__setattr__("_reverse_fkmap", reverse_fkmap)

    def gen_fkmap(self):
        fkmap = {}

        all_field_names = self._wrapped_class.DESCRIPTOR.fields_by_name.keys()

        for (name, field) in self._wrapped_class.DESCRIPTOR.fields_by_name.items():
           if name.endswith("_id"):
               foreignKey = field.GetOptions().Extensions._FindExtensionByName("xos.foreignKey")
               fk = field.GetOptions().Extensions[foreignKey]
               if fk and fk.modelName:
                   fkmap[name[:-3]] = {"src_fieldName": name, "modelName": fk.modelName, "kind": "fk"}
               else:
                   # If there's a corresponding _type_id field, then see if this
                   # is a generic foreign key.
                   type_name = name[:-3] + "_type_id"
                   if type_name in all_field_names:
                       fkmap[name[:-3]] = {"src_fieldName": name, "ct_fieldName": type_name, "kind": "generic_fk"}

        return fkmap

    def gen_reverse_fkmap(self):
        reverse_fkmap = {}

        for (name, field) in self._wrapped_class.DESCRIPTOR.fields_by_name.items():
           if name.endswith("_ids"):
               reverseForeignKey = field.GetOptions().Extensions._FindExtensionByName("xos.reverseForeignKey")
               fk = field.GetOptions().Extensions[reverseForeignKey]
               if fk:
                   reverse_fkmap[name[:-4]] = {"src_fieldName": name, "modelName": fk.modelName}

        return reverse_fkmap

    def fk_resolve(self, name):
        if name in self.cache:
            return make_ORMWrapper(self.cache[name], self.stub)

        fk_entry = self._fkmap[name]
        fk_kind = fk_entry["kind"]
        fk_id = getattr(self, fk_entry["src_fieldName"])

        if not fk_id:
            return None

        if fk_kind=="fk":
            id=self.stub.make_ID(id=fk_id)
            dest_model = self.stub.invoke("Get%s" % fk_entry["modelName"], id)

        elif fk_kind=="generic_fk":
            dest_model = self.stub.genericForeignKeyResolve(getattr(self, fk_entry["ct_fieldName"]), fk_id)._wrapped_class

        else:
            raise Exception("unknown fk_kind")

        self.cache[name] = dest_model

        return make_ORMWrapper(dest_model, self.stub)

    def reverse_fk_resolve(self, name):
        if name not in self.reverse_cache:
            fk_entry = self._reverse_fkmap[name]
            self.cache[name] = ORMLocalObjectManager(self.stub, fk_entry["modelName"], getattr(self, fk_entry["src_fieldName"]))

        return self.cache[name]

    def fk_set(self, name, model):
        fk_entry = self._fkmap[name]
        fk_kind = fk_entry["kind"]
        id = model.id
        setattr(self._wrapped_class, fk_entry["src_fieldName"], id)

        if fk_kind=="generic_fk":
            setattr(self._wrapped_class, fk_entry["ct_fieldName"], model.self_content_type_id)

        # XXX setting the cache here is a problematic, since the cached object's
        # reverse foreign key pointers will not include the reference back
        # to this object. Instead of setting the cache, let's poison the name
        # and throw an exception if someone tries to get it.

        # To work around this, explicitly call reset_cache(fieldName) and
        # the ORM will reload the object.

        self.poisoned[name] = True

    def __getattr__(self, name, *args, **kwargs):
        # note: getattr is only called for attributes that do not exist in
        #       self.__dict__

        # pk is a synonym for id
        if (name == "pk"):
            name = "id"

        if name in self.poisoned.keys():
            # see explanation in fk_set()
            raise Exception("foreign key was poisoned")

        if name in self._fkmap.keys():
            return self.fk_resolve(name)

        if name in self._reverse_fkmap.keys():
            return self.reverse_fk_resolve(name)

        return getattr(self._wrapped_class, name, *args, **kwargs)

    def __setattr__(self, name, value):
        if name in self._fkmap.keys():
            self.fk_set(name, value)
        elif name in self.__dict__:
            super(ORMWrapper,self).__setattr__(name, value)
        else:
            setattr(self._wrapped_class, name, value)

    def __repr__(self):
        return self._wrapped_class.__repr__()

    def invalidate_cache(self, name=None):
        if name:
            if name in self.cache:
                del self.cache[name]
            if name in self.reverse_cache:
                del self.reverse_cache[name]
            if name in self.poisoned:
                del self.poisoned[name]
        else:
            self.cache.clear()
            self.reverse_cache.clear()
            self.poisoned.clear()

    def save(self, update_fields=None):
        if self.is_new:
           new_class = self.stub.invoke("Create%s" % self._wrapped_class.__class__.__name__, self._wrapped_class)
           self._wrapped_class = new_class
           self.is_new = False
        else:
           metadata = []
           if update_fields:
               metadata.append( ("update_fields", ",".join(update_fields)) )
           self.stub.invoke("Update%s" % self._wrapped_class.__class__.__name__, self._wrapped_class, metadata=metadata)

    def delete(self):
        id = self.stub.make_ID(id=self._wrapped_class.id)
        self.stub.invoke("Delete%s" % self._wrapped_class.__class__.__name__, id)

    def tologdict(self):
        try:
            d = {'model_name':self.__class__.__name__, 'pk': self.pk}
        except:
            d = {}

        return d

    @property
    def model_name(self):
        return self._wrapped_class.__class__.__name__

    @property
    def ansible_tag(self):
        return "%s_%s" % (self._wrapped_class.__class__.__name__, self.id)

#    @property
#    def self_content_type_id(self):
#        return getattr(self.stub, self._wrapped_class.__class__.__name__).content_type_id

class ORMQuerySet(list):
    """ Makes lists look like django querysets """
    def first(self):
        if len(self)>0:
            return self[0]
        else:
            return None

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
        for id in self._idList:
            models.append(self._stub.invoke("Get%s" % self._modelName, self._stub.make_ID(id=id)))

        self._cache = models

        return models

    def all(self):
        models = self.resolve_queryset()
        return [make_ORMWrapper(x,self._stub) for x in models]

class ORMObjectManager(object):
    """ Manages a remote list of objects """

    # constants better agree with common.proto
    SYNCHRONIZER_DIRTY_OBJECTS = 2;
    SYNCHRONIZER_DELETED_OBJECTS = 3;

    def __init__(self, stub, modelName, packageName):
        self._stub = stub
        self._modelName = modelName
        self._packageName = packageName

    def wrap_single(self, obj):
        return make_ORMWrapper(obj, self._stub)

    def wrap_list(self, obj):
        result=[]
        for item in obj.items:
            result.append(make_ORMWrapper(item, self._stub))
        return ORMQuerySet(result)

    def all(self):
        return self.wrap_list(self._stub.invoke("List%s" % self._modelName, Empty()))

    def first(self):
        objs=self.wrap_list(self._stub.invoke("List%s" % self._modelName, Empty()))
        if not objs:
            return None
        return objs[0]

    def filter(self, **kwargs):
        q = self._stub.make_Query()
        q.kind = q.DEFAULT

        for (name, val) in kwargs.items():
            el = q.elements.add()

            if name.endswith("__gt"):
                name = name[:-4]
                el.operator = el.GREATER_THAN
            elif name.endswith("__gte"):
                name = name[:-5]
                el.operator = el.GREATER_THAN_OR_EQUAL
            elif name.endswith("__lt"):
                name = name[:-4]
                el.operator = el.LESS_THAN
            elif name.endswith("__lte"):
                name = name[:-5]
                el.operator = el.LESS_THAN_OR_EQUAL
            else:
                el.operator = el.EQUAL

            el.name = name
            if isinstance(val, int):
                el.iValue = val
            else:
                el.sValue = val

        return self.wrap_list(self._stub.invoke("Filter%s" % self._modelName, q))

    def filter_special(self, kind):
        q = self._stub.make_Query()
        q.kind = kind
        return self.wrap_list(self._stub.invoke("Filter%s" % self._modelName, q))

    def get(self, **kwargs):
        if kwargs.keys() == ["id"]:
            # the fast and easy case, look it up by id
            return self.wrap_single(self._stub.invoke("Get%s" % self._modelName, self._stub.make_ID(id=kwargs["id"])))
        else:
            # the slightly more difficult case, filter and return the first item
            objs = self.filter(**kwargs)
            return objs[0]

    def new(self, **kwargs):
        cls = self._stub.all_grpc_classes[self._modelName]
        return make_ORMWrapper(cls(), self._stub, is_new=True)

class ORMModelClass(object):
    def __init__(self, stub, model_name, package_name):
        self.model_name = model_name
        self._stub = stub
        self.objects = ORMObjectManager(stub, model_name, package_name)

    @property
    def __name__(self):
        return self.model_name

    @property
    def content_type_id(self):
        return self._stub.reverse_content_type_map[self.model_name]

class ORMStub(object):
    def __init__(self, stub, package_name, invoker=None, caller_kind="grpcapi"):
        self.grpc_stub = stub
        self.all_model_names = []
        self.all_grpc_classes = {}
        self.content_type_map = {}
        self.reverse_content_type_map = {}
        self.invoker = invoker
        self.caller_kind = caller_kind

        for name in dir(stub):
           if name.startswith("Get"):
               model_name = name[3:]
               setattr(self,model_name, ORMModelClass(self, model_name, package_name))

               self.all_model_names.append(model_name)

               grpc_class = _sym_db._classes["%s.%s" % (package_name, model_name)]
               self.all_grpc_classes[model_name] = grpc_class

               ct = grpc_class.DESCRIPTOR.GetOptions().Extensions._FindExtensionByName("xos.contentTypeId")
               if ct:
                   ct = grpc_class.DESCRIPTOR.GetOptions().Extensions[ct]
                   if ct:
                       self.content_type_map[ct] = model_name
                       self.reverse_content_type_map[model_name] = ct

    def genericForeignKeyResolve(self, content_type_id, id):
        model_name = self.content_type_map[content_type_id]
        model = getattr(self, model_name)
        return model.objects.get(id=id)

    def listObjects(self):
        return self.all_model_names

    def add_default_metadata(self, metadata):
        default_metadata = [ ("caller_kind", self.caller_kind) ]

        # build up a list of metadata keys we already have
        md_keys=[x[0] for x in metadata]

        # add any defaults that we don't already have
        for md in default_metadata:
            if md[0] not in md_keys:
                metadata.append( (md[0], md[1]) )

    def invoke(self, name, request, metadata=[]):
        self.add_default_metadata(metadata)

        if self.invoker:
            # Hook in place to call Chameleon's invoke method, as soon as we
            # have rewritten the synchronizer to use reactor.
            return self.invoker.invoke(self.grpc_stub.__class__, name, request, metadata={}).result[0]
        else:
            # Our own retry mechanism. This works fine if there is a temporary
            # failure in connectivity, but does not re-download gRPC schema.
            while True:
                backoff = [0.5, 1, 2, 4, 8]
                try:
                    method = getattr(self.grpc_stub, name)
                    return method(request, metadata=metadata)
                except grpc._channel._Rendezvous, e:
                    code = e.code()
                    if code == grpc.StatusCode.UNAVAILABLE:
                        if not backoff:
                            raise Exception("No more retries on %s" % name)
                        time.sleep(backoff.pop(0))
                    else:
                        raise
                except:
                    raise

    def make_ID(self, id):
        return _sym_db._classes["xos.ID"](id=id)

    def make_Query(self):
        return _sym_db._classes["xos.Query"]()

def register_convenience_wrapper(class_name, wrapper):
    global convenience_wrappers

    convenience_wrappers[class_name] = wrapper

def make_ORMWrapper(wrapped_class, *args, **kwargs):
    if wrapped_class.__class__.__name__ in convenience_wrappers:
        cls = convenience_wrappers[wrapped_class.__class__.__name__]
    else:
        cls = ORMWrapper

    return cls(wrapped_class, *args, **kwargs)

import convenience.instance
import convenience.cordsubscriberroot
import convenience.volttenant
import convenience.vsgtenant
import convenience.vroutertenant

