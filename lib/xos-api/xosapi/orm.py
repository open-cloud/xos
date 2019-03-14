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

from __future__ import absolute_import, print_function

import imp
import os
import sys
import threading
import time
import traceback

from multistructlog import create_logger
from xosconfig import Config

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

log = create_logger(Config().get("logging"))

convenience_wrappers = {}


def get_synchronizer_function():
    """
    Find the topmost synchronizer-specific function in the call stack
    """
    result = None
    for file, line, func, stmt in traceback.extract_stack():
        if file.startswith("/opt/xos/synchronizers"):
            if not result:
                result = "%s:%s()" % (file, func)
            if not file.startswith("/opt/xos/synchronizers/new_base"):
                result = "%s:%s()" % (file, func)
                break
    return result


class ORMGenericContentNotFoundException(Exception):
    pass


class ORMGenericObjectNotFoundException(Exception):
    pass


class ORMWrapper(object):
    """ Wraps a protobuf object to provide ORM features """

    def __init__(self, wrapped_class, stub, is_new=False):
        super(ORMWrapper, self).__setattr__("_wrapped_class", wrapped_class)
        super(ORMWrapper, self).__setattr__("stub", stub)
        super(ORMWrapper, self).__setattr__("cache", {})
        super(ORMWrapper, self).__setattr__("reverse_cache", {})
        super(ORMWrapper, self).__setattr__("synchronizer_step", None)
        super(ORMWrapper, self).__setattr__("dependent", None)
        super(ORMWrapper, self).__setattr__("is_new", is_new)
        super(ORMWrapper, self).__setattr__("post_save_fixups", [])
        fkmap = self.gen_fkmap()
        super(ORMWrapper, self).__setattr__("_fkmap", fkmap)
        reverse_fkmap = self.gen_reverse_fkmap()
        super(ORMWrapper, self).__setattr__("_reverse_fkmap", reverse_fkmap)
        super(ORMWrapper, self).__setattr__("_initial", self._dict)

    def fields_differ(self, f1, f2):
        return f1 != f2

    @property
    def _dict(self):
        """ Return a dictionary of {fieldname: fieldvalue} for the object.

            This differs for the xos-core implementation of XOSBase. For new object, XOSBase will include field names
            that are set to default values. ORM ignores fields that are set to default values.
        """
        d = {}
        for (fieldDesc, val) in self._wrapped_class.ListFields():
            name = fieldDesc.name
            d[name] = val
        return d

    @property
    def diff(self):
        d1 = self._initial
        d2 = self._dict
        all_field_names = list(self._wrapped_class.DESCRIPTOR.fields_by_name.keys())
        diffs = []
        for k in all_field_names:
            if d1.get(k, None) != d2.get(k, None):
                diffs.append((k, (d1.get(k, None), d2.get(k, None))))

        # diffs = [(k, (v, d2[k])) for k, v in d1.items() if self.fields_differ(v,d2[k])]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        """ Return the list of changed fields.

            This differs for the xos-core implementation of XOSBase. For new object, XOSBase will include field names
            that are set to default values.
        """
        if self.is_new:
            return list(self._dict.keys())
        return list(self.diff.keys())

    def has_field_changed(self, field_name):
        return field_name in list(self.diff.keys())

    def get_field_diff(self, field_name):
        return self.diff.get(field_name, None)

    def recompute_initial(self):
        self._initial = self._dict

    def save_changed_fields(self, always_update_timestamp=False):
        if self.has_changed:
            update_fields = self.changed_fields
            if always_update_timestamp and "updated" not in update_fields:
                update_fields.append("updated")
            self.save(
                update_fields=sorted(update_fields),
                always_update_timestamp=always_update_timestamp,
            )

    def create_attr(self, name, value=None):
        """ setattr(self, ...) will fail for attributes that don't exist in the
            wrapped grpc class. This is by design. However, if someone really
            does want to attach a new attribute to this class, then they can
            call create_attr()
        """
        super(ORMWrapper, self).__setattr__(name, value)

    def get_generic_foreignkeys(self):
        """ this is a placeholder until generic foreign key support is added
            to xproto.
        """
        return []

    def gen_fkmap(self):
        fkmap = {}

        all_field_names = list(self._wrapped_class.DESCRIPTOR.fields_by_name.keys())

        for (name, field) in self._wrapped_class.DESCRIPTOR.fields_by_name.items():
            if name.endswith("_id"):
                foreignKey = field.GetOptions().Extensions._FindExtensionByName(
                    "xos.foreignKey"
                )
                fk = field.GetOptions().Extensions[foreignKey]
                if fk and fk.modelName:
                    fkdict = {
                        "src_fieldName": name,
                        "modelName": fk.modelName,
                        "kind": "fk",
                    }
                    if fk.reverseFieldName:
                        fkdict["reverse_fieldName"] = fk.reverseFieldName
                    fkmap[name[:-3]] = fkdict
                else:
                    # If there's a corresponding _type_id field, then see if this
                    # is a generic foreign key.
                    type_name = name[:-3] + "_type_id"
                    if type_name in all_field_names:
                        fkmap[name[:-3]] = {
                            "src_fieldName": name,
                            "ct_fieldName": type_name,
                            "kind": "generic_fk",
                        }

        for gfk in self.get_generic_foreignkeys():
            fkmap[gfk["name"]] = {
                "src_fieldName": gfk["id"],
                "ct_fieldName": gfk["content_type"],
                "kind": "generic_fk",
            }

        return fkmap

    def gen_reverse_fkmap(self):
        reverse_fkmap = {}

        for (name, field) in self._wrapped_class.DESCRIPTOR.fields_by_name.items():
            if name.endswith("_ids"):
                reverseForeignKey = field.GetOptions().Extensions._FindExtensionByName(
                    "xos.reverseForeignKey"
                )
                fk = field.GetOptions().Extensions[reverseForeignKey]
                if fk and fk.modelName:
                    reverse_fkmap[name[:-4]] = {
                        "src_fieldName": name,
                        "modelName": fk.modelName,
                        "writeable": False,
                    }
                else:
                    manyToManyForeignKey = field.GetOptions().Extensions._FindExtensionByName(
                        "xos.manyToManyForeignKey"
                    )
                    fk = field.GetOptions().Extensions[manyToManyForeignKey]
                    if fk and fk.modelName:
                        reverse_fkmap[name[:-4]] = {
                            "src_fieldName": name,
                            "modelName": fk.modelName,
                            "writeable": True,
                        }

        return reverse_fkmap

    def fk_resolve(self, name):
        if name in self.cache:
            return self.cache[name]

        fk_entry = self._fkmap[name]
        fk_kind = fk_entry["kind"]
        fk_id = getattr(self, fk_entry["src_fieldName"])

        if not fk_id:
            return None

        if fk_kind == "fk":
            id = self.stub.make_ID(id=fk_id)
            dest_model = self.stub.invoke("Get%s" % fk_entry["modelName"], id)

        elif fk_kind == "generic_fk":
            dest_model = self.stub.genericForeignKeyResolve(
                getattr(self, fk_entry["ct_fieldName"]), fk_id
            )._wrapped_class

        else:
            raise Exception("unknown fk_kind")

        dest_model = make_ORMWrapper(dest_model, self.stub)
        self.cache[name] = dest_model

        return dest_model

    def reverse_fk_resolve(self, name):
        if name not in self.reverse_cache:
            fk_entry = self._reverse_fkmap[name]
            self.reverse_cache[name] = ORMLocalObjectManager(
                self.stub,
                fk_entry["modelName"],
                getattr(self, fk_entry["src_fieldName"]),
                fk_entry["writeable"],
            )

        return self.reverse_cache[name]

    def fk_set(self, name, model):
        fk_entry = self._fkmap[name]
        fk_kind = fk_entry["kind"]
        if model:
            id = model.id
        else:
            id = 0
        setattr(self._wrapped_class, fk_entry["src_fieldName"], id)

        if fk_kind == "generic_fk":
            setattr(
                self._wrapped_class,
                fk_entry["ct_fieldName"],
                model.self_content_type_id,
            )

        if name in self.cache:
            old_model = self.cache[name]
            if fk_entry.get("reverse_fieldName"):
                # Note this fk change so that we can update the destination model after we save.
                self.post_save_fixups.append(
                    {
                        "src_fieldName": fk_entry["src_fieldName"],
                        "dest_id": id,
                        "dest_model": old_model,
                        "remove": True,
                        "reverse_fieldName": fk_entry.get("reverse_fieldName"),
                    }
                )
            del self.cache[name]

        if model:
            self.cache[name] = model
            if fk_entry.get("reverse_fieldName"):
                # Note this fk change so that we can update the destination model after we save.
                self.post_save_fixups.append(
                    {
                        "src_fieldName": fk_entry["src_fieldName"],
                        "dest_id": id,
                        "dest_model": model,
                        "remove": False,
                        "reverse_fieldName": fk_entry.get("reverse_fieldName"),
                    }
                )
        elif name in self.cache:
            del self.cache[name]

    def do_post_save_fixups(self):
        # Perform post-save foreign key fixups.
        # Fixup the models that we've set a foreign key to so that their in-memory representation has the correct
        # reverse foreign key back to us. We can only do this after a save, because self.id isn't known until
        # after save.
        # See unit test test_foreign_key_set_without_invalidate
        for fixup in self.post_save_fixups:
            model = fixup["dest_model"]
            reverse_fieldName_ids = fixup["reverse_fieldName"] + "_ids"
            if not hasattr(model, reverse_fieldName_ids):
                continue
            if fixup["remove"]:
                reverse_ids = getattr(model, reverse_fieldName_ids)
                if self.id in reverse_ids:
                    reverse_ids.remove(self.id)
            else:
                reverse_ids = getattr(model, reverse_fieldName_ids)
                if self.id not in reverse_ids:
                    reverse_ids.append(self.id)
            model.invalidate_cache(fixup["reverse_fieldName"])
        self.post_save_fixups = []

    def __getattr__(self, name, *args, **kwargs):
        # note: getattr is only called for attributes that do not exist in
        #       self.__dict__

        # pk is a synonym for id
        if name == "pk":
            name = "id"

        if name in list(self._fkmap.keys()):
            return self.fk_resolve(name)

        if name in list(self._reverse_fkmap.keys()):
            return self.reverse_fk_resolve(name)

        try:
            # When sending a reply, XOS will leave the field unset if it is None in the data model. If
            # HasField(<fieldname>)==False for an existing object, then the caller can infer that field was set to
            # None.
            if (not self.is_new) and (not self._wrapped_class.HasField(name)):
                return None
        except ValueError:
            # ValueError is thrown if the field does not exist. We will handle that case in the getattr() below.
            pass

        return getattr(self._wrapped_class, name, *args, **kwargs)

    def __setattr__(self, name, value):
        if name in list(self._fkmap.keys()):
            self.fk_set(name, value)
        elif name in self.__dict__:
            super(ORMWrapper, self).__setattr__(name, value)
        elif value is None:
            # When handling requests, XOS interprets gRPC HasField(<fieldname>)==False to indicate that the caller
            # has not set the field and wants it to continue to use its existing (or default) value. That leaves us
            # with no easy way to support setting a field to None.
            raise ValueError("Setting a non-foreignkey field to None is not supported")
        else:
            setattr(self._wrapped_class, name, value)

    def __repr__(self):
        class_name = self._wrapped_class.__class__.__name__
        id = getattr(self._wrapped_class, "id", "noid")
        name = getattr(self._wrapped_class, "name", None)
        if name:
            return "<%s: %s>" % (class_name, name)
        else:
            return "<%s: id-%s>" % (class_name, id)

    def __str__(self):
        class_name = self._wrapped_class.__class__.__name__
        id = getattr(self._wrapped_class, "id", "noid")
        name = getattr(self._wrapped_class, "name", None)
        if name:
            return name
        else:
            return "%s-%s" % (class_name, id)

    def dumpstr(self):
        return self._wrapped_class.__repr__()

    def dump(self):
        print(self.dumpstr())

    def invalidate_cache(self, name=None):
        if name:
            if name in self.cache:
                del self.cache[name]
            if name in self.reverse_cache:
                del self.reverse_cache[name]
        else:
            self.cache.clear()
            self.reverse_cache.clear()

    def save(
        self,
        update_fields=None,
        always_update_timestamp=False,
        is_sync_save=False,
        is_policy_save=False,
    ):
        classname = self._wrapped_class.__class__.__name__
        if self.is_new:
            log.debug(
                "save(): is new",
                classname=classname,
                syncstep=get_synchronizer_function(),
            )
            new_class = self.stub.invoke("Create%s" % classname, self._wrapped_class)
            self._wrapped_class = new_class
            self.is_new = False
        else:
            if self.has_changed:
                log.debug(
                    "save(): updated",
                    classname=classname,
                    changed_fields=self.changed_fields,
                    syncstep=get_synchronizer_function(),
                )
            else:
                log.debug(
                    "save(): no changes",
                    classname=classname,
                    syncstep=get_synchronizer_function(),
                )
            metadata = []
            if update_fields:
                metadata.append(("update_fields", ",".join(update_fields)))
            if always_update_timestamp:
                metadata.append(("always_update_timestamp", "1"))
            if is_policy_save:
                metadata.append(("is_policy_save", "1"))
            if is_sync_save:
                metadata.append(("is_sync_save", "1"))
            self.stub.invoke(
                "Update%s" % classname, self._wrapped_class, metadata=metadata
            )
        self.do_post_save_fixups()

        # Now that object has saved, reset our initial state for diff calculation
        self.recompute_initial()

    def delete(self):
        id = self.stub.make_ID(id=self._wrapped_class.id)
        self.stub.invoke("Delete%s" % self._wrapped_class.__class__.__name__, id)

    def tologdict(self):
        try:
            d = {"model_name": self._wrapped_class.__class__.__name__, "pk": self.pk}
        except BaseException:
            d = {}

        return d

    @property
    def leaf_model(self):
        # Easy case - this model is already the leaf
        if self.leaf_model_name == self._wrapped_class.__class__.__name__:
            return self

        # This model is not the leaf, so use the stub to fetch the leaf model
        return getattr(self.stub, self.leaf_model_name).objects.get(id=self.id)

    @property
    def model_name(self):
        return self._wrapped_class.__class__.__name__

    @property
    def ansible_tag(self):
        return "%s_%s" % (self._wrapped_class.__class__.__name__, self.id)


class ORMQuerySet(list):
    """ Makes lists look like django querysets """

    def first(self):
        if len(self) > 0:
            return self[0]
        else:
            return None

    def exists(self):
        return len(self) > 0


class ORMLocalObjectManager(object):
    """ Manages a local list of objects """

    def __init__(self, stub, modelName, idList, writeable):
        self._stub = stub
        self._modelName = modelName
        self._idList = idList
        self._writeable = writeable
        self._cache = None

    def resolve_queryset(self):
        if self._cache is not None:
            return self._cache

        models = []
        for id in self._idList:
            models.append(
                self._stub.invoke("Get%s" % self._modelName, self._stub.make_ID(id=id))
            )

        self._cache = models

        return models

    def all(self):
        models = self.resolve_queryset()
        return [make_ORMWrapper(x, self._stub) for x in models]

    def exists(self):
        return len(self._idList) > 0

    def count(self):
        return len(self._idList)

    def first(self):
        if self._idList:
            model = make_ORMWrapper(
                self._stub.invoke(
                    "Get%s" % self._modelName, self._stub.make_ID(id=self._idList[0])
                ),
                self._stub,
            )
            return model
        else:
            return None

    def add(self, model):
        if not self._writeable:
            raise Exception("Only ManyToMany lists are writeable")

        if isinstance(model, int):
            id = model
        else:
            if not model.id:
                raise Exception("Model %s has no id" % model)
            id = model.id

        self._idList.append(id)

    def remove(self, model):
        if not self._writeable:
            raise Exception("Only ManyToMany lists are writeable")

        if isinstance(model, int):
            id = model
        else:
            if not model.id:
                raise Exception("Model %s has no id" % model)
            id = model.id

        self._idList.remove(id)


class ORMObjectManager(object):
    """ Manages a remote list of objects """

    # constants better agree with common.proto
    DEFAULT = 0
    ALL = 1
    SYNCHRONIZER_DIRTY_OBJECTS = 2
    SYNCHRONIZER_DELETED_OBJECTS = 3
    SYNCHRONIZER_DIRTY_POLICIES = 4
    SYNCHRONIZER_DELETED_POLICIES = 5

    def __init__(self, stub, modelName, packageName, kind=0):
        self._stub = stub
        self._modelName = modelName
        self._packageName = packageName
        self._kind = kind

    def wrap_single(self, obj):
        return make_ORMWrapper(obj, self._stub)

    def wrap_list(self, obj):
        result = []
        for item in obj.items:
            result.append(make_ORMWrapper(item, self._stub))
        return ORMQuerySet(result)

    def all(self):
        if self._kind == self.DEFAULT:
            return self.wrap_list(
                self._stub.invoke("List%s" % self._modelName, self._stub.make_empty())
            )
        else:
            return self.filter()

    def first(self):
        objs = self.all()
        if not objs:
            return None
        return objs[0]

    def filter(self, **kwargs):
        q = self._stub.make_Query()
        q.kind = self._kind

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
            elif name.endswith("__iexact"):
                name = name[:-8]
                el.operator = el.IEXACT
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
        if list(kwargs.keys()) == ["id"]:
            # the fast and easy case, look it up by id
            return self.wrap_single(
                self._stub.invoke(
                    "Get%s" % self._modelName, self._stub.make_ID(id=kwargs["id"])
                )
            )
        else:
            # the slightly more difficult case, filter and return the first item
            objs = self.filter(**kwargs)
            return objs[0]

    def new(self, **kwargs):
        if self._kind != ORMObjectManager.DEFAULT:
            raise Exception(
                "Creating objects is only supported by the DEFAULT object manager"
            )

        cls = self._stub.all_grpc_classes[self._modelName]
        o = make_ORMWrapper(cls(), self._stub, is_new=True)
        for (k, v) in kwargs.items():
            setattr(o, k, v)
        o.recompute_initial()
        return o


class ORMModelClass(object):
    def __init__(self, stub, model_name, package_name):
        self.model_name = model_name
        self._stub = stub
        self.objects = ORMObjectManager(stub, model_name, package_name)
        self.deleted_objects = ORMObjectManager(
            stub,
            model_name,
            package_name,
            ORMObjectManager.SYNCHRONIZER_DELETED_OBJECTS,
        )

    @property
    def __name__(self):
        return self.model_name

    @property
    def content_type_id(self):
        return self._stub.reverse_content_type_map[self.model_name]

    def __call__(self, *args, **kwargs):
        return self.objects.new(*args, **kwargs)


class ORMStub(object):
    def __init__(
        self,
        stub,
        protos,
        package_name,
        invoker=None,
        caller_kind="grpcapi",
        empty=None,
        enable_backoff=True,
        restart_on_disconnect=False,
    ):
        self.grpc_stub = stub
        self.protos = protos
        self.common_protos = protos.common__pb2
        self.all_model_names = []
        self.all_grpc_classes = {}
        self.content_type_map = {}
        self.reverse_content_type_map = {}
        self.invoker = invoker
        self.caller_kind = caller_kind
        self.enable_backoff = enable_backoff
        self.restart_on_disconnect = restart_on_disconnect

        if not empty:
            empty = self.protos.google_dot_protobuf_dot_empty__pb2.Empty
        self._empty = empty

        for name in dir(stub):
            if name.startswith("Get"):
                model_name = name[3:]
                setattr(self, model_name, ORMModelClass(self, model_name, package_name))

                self.all_model_names.append(model_name)

                grpc_class = getattr(self.protos, model_name)
                self.all_grpc_classes[model_name] = grpc_class

                ct = grpc_class.DESCRIPTOR.GetOptions().Extensions._FindExtensionByName(
                    "xos.contentTypeId"
                )
                if ct:
                    ct = grpc_class.DESCRIPTOR.GetOptions().Extensions[ct]
                    if ct:
                        self.content_type_map[ct] = model_name
                        self.reverse_content_type_map[model_name] = ct

    def genericForeignKeyResolve(self, content_type_id, id):
        if content_type_id.endswith("_decl"):
            content_type_id = content_type_id[:-5]

        if content_type_id not in self.content_type_map:
            raise ORMGenericContentNotFoundException(
                "Content_type %s not found in self.content_type_map" % content_type_id
            )

        model_name = self.content_type_map[content_type_id]

        model = getattr(self, model_name)
        objs = model.objects.filter(id=id)
        if not objs:
            raise ORMGenericObjectNotFoundException(
                "Object %s of model %s was not found" % (id, model_name)
            )

        return model.objects.get(id=id)

    def add_default_metadata(self, metadata):
        default_metadata = [("caller_kind", self.caller_kind)]

        # introspect to see if we're running from a synchronizer thread
        if getattr(threading.current_thread(), "is_sync_thread", False):
            default_metadata.append(("is_sync_save", "1"))

        # introspect to see if we're running from a model_policy thread
        if getattr(threading.current_thread(), "is_policy_thread", False):
            default_metadata.append(("is_policy_save", "1"))

        # build up a list of metadata keys we already have
        md_keys = [x[0] for x in metadata]

        # add any defaults that we don't already have
        for md in default_metadata:
            if md[0] not in md_keys:
                metadata.append((md[0], md[1]))

    def invoke(self, name, request, metadata=[]):
        self.add_default_metadata(metadata)

        if self.invoker:
            # Hook in place to call Chameleon's invoke method, as soon as we
            # have rewritten the synchronizer to use reactor.
            return self.invoker.invoke(
                self.grpc_stub.__class__, name, request, metadata={}
            ).result[0]
        elif self.enable_backoff:
            # Our own retry mechanism. This works fine if there is a temporary
            # failure in connectivity, but does not re-download gRPC schema.
            import grpc

            backoff = [0.5, 1, 2, 4, 8]
            while True:
                try:
                    method = getattr(self.grpc_stub, name)
                    return method(request, metadata=metadata)
                except grpc._channel._Rendezvous as e:
                    code = e.code()
                    if code == grpc.StatusCode.UNAVAILABLE:
                        if self.restart_on_disconnect:
                            # This is a blunt technique... We lost connectivity to the core, and we don't know that
                            # the core is still serving up the same models it was when we established connectivity,
                            # so restart the synchronizer.
                            # TODO: Hash check on the core models to tell if something changed would be better.
                            os.execv(sys.executable, ["python"] + sys.argv)
                        if not backoff:
                            raise Exception("No more retries on %s" % name)
                        time.sleep(backoff.pop(0))
                    else:
                        raise
                except BaseException:
                    raise
        else:
            method = getattr(self.grpc_stub, name)
            return method(request, metadata=metadata)

    def make_ID(self, id):
        return getattr(self.common_protos, "ID")(id=id)

    def make_empty(self):
        return self._empty()

    def make_Query(self):
        return getattr(self.common_protos, "Query")()

    def listObjects(self):
        return self.all_model_names


def register_convenience_wrapper(class_name, wrapper):
    global convenience_wrappers

    convenience_wrappers[class_name] = wrapper


def make_ORMWrapper(wrapped_class, *args, **kwargs):
    cls = None

    if (not cls) and wrapped_class.__class__.__name__ in convenience_wrappers:
        cls = convenience_wrappers[wrapped_class.__class__.__name__]

    if not cls:
        # Search the list of class names for this model to see if we have any applicable wrappers. The list is always
        # sorted from most specific to least specific, so the first one we find will automatically be the most relevant
        # one. If we don't find any, then default to ORMWrapper

        # Note: Only works on objects that have been fetched from the server, not objects that are created on the
        # client. This is because wrapped_class.class_names is filled in by the server.

        # TODO(smbaker): Ought to be able to make this work with newly created objects after they are saved.

        for name in wrapped_class.class_names.split(","):
            if name in convenience_wrappers:
                cls = convenience_wrappers[name]

    if not cls:
        cls = ORMWrapper

    return cls(wrapped_class, *args, **kwargs)


def import_convenience_methods():
    # The ORM has several built-in convenience methods that are contained here
    lib_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    base_convenience_dir = os.path.join(lib_dir, "convenience")

    # Service convenience methods are placed here during dynamicload
    service_convenience_dir = "/var/run/xosapi/convenience"

    for api_convenience_dir in [base_convenience_dir, service_convenience_dir]:
        log.info("Loading convenience methods", api_convenience_dir=api_convenience_dir)

        if not os.path.exists(api_convenience_dir):
            log.info("No convenience methods found", api_convenience_dir=api_convenience_dir)
            continue

        for file in os.listdir(api_convenience_dir):
            if file.endswith(".py") and "test" not in file:
                pathname = os.path.join(api_convenience_dir, file)
                try:
                    log.debug("Loading: %s" % file)
                    imp.load_source(file[:-3], pathname)
                except Exception:
                    log.exception(
                        "Cannot import api convenience method for: %s, %s"
                        % (file[:-3], pathname)
                    )
