
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


import base64
import datetime
import inspect
import pytz
import threading
import time
from protos import xos_pb2
from google.protobuf.empty_pb2 import Empty
import grpc

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate as django_authenticate
from django.db.models import F, Q
from core.models import *
from xos.exceptions import *

from importlib import import_module
from django.conf import settings


class XOSDefaultSecurityContext(object):
    grant_access = True
    write_access = True
    read_access = True


xos_anonymous_site = Site(
    name='XOS Anonymous Site',
    enabled=True,
    hosts_nodes=False,
    hosts_users=True,
    login_base='xos',
    abbreviated_name='xos-anonymous')

xos_anonymous_user = User(
    username='XOS Anonymous User',
    email='xos@example.com',
    is_admin=False,
    site=xos_anonymous_site)

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


def translate_exceptions(function):
    """ this decorator translates XOS exceptions to grpc status codes """
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            if "context" in kwargs:
                context = kwargs["context"]
            else:
                context = args[2]

            if hasattr(e, 'json_detail'):
                context.set_details(e.json_detail)
            elif hasattr(e, 'detail'):
                context.set_details(e.detail)

            if (isinstance(e, XOSPermissionDenied)):
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            elif (isinstance(e, XOSValidationError)):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            elif (isinstance(e, XOSNotAuthenticated)):
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            raise
    return wrapper


bench_tStart = time.time()
bench_ops = 0


def benchmark(function):
    """ this decorator will report gRPC benchmark statistics every 10 seconds """
    def wrapper(*args, **kwargs):
        global bench_tStart
        global bench_ops
        result = function(*args, **kwargs)
        bench_ops = bench_ops + 1
        elap = time.time() - bench_tStart
        if (elap >= 10):
            print "performance %d" % (bench_ops / elap)
            bench_ops = 0
            bench_tStart = time.time()
        return result
    return wrapper


class CachedAuthenticator(object):
    """ Django Authentication is very slow (~ 10 ops/second), so cache
        authentication results and reuse them.
    """

    def __init__(self):
        self.cached_creds = {}
        self.timeout = 10          # keep cache entries around for 10s
        # lock to keep multiple callers from trimming at the same time
        self.lock = threading.Lock()

    def authenticate(self, username, password):
        self.trim()

        key = "%s:%s" % (username, password)
        cred = self.cached_creds.get(key, None)
        if cred:
            user = User.objects.filter(id=cred["user_id"])
            if user:
                user = user[0]
                # print "cached authenticated %s:%s as %s" % (username,
                # password, user)
                return user

        user = django_authenticate(username=username, password=password)
        if user:
            # print "django authenticated %s:%s as %s" % (username, password,
            # user)
            self.cached_creds[key] = {
                "timeout": time.time() + self.timeout,
                "user_id": user.id}

        return user

    def trim(self):
        """ Delete all cache entries that have expired """
        self.lock.acquire()
        for (k, v) in list(self.cached_creds.items()):
            if time.time() > v["timeout"]:
                del self.cached_creds[k]
        self.lock.release()


cached_authenticator = CachedAuthenticator()


class XOSAPIHelperMixin(object):
    def __init__(self):
        import django.apps

        self.models = {}
        for model in django.apps.apps.get_models():
            self.models[model.__name__] = model

    def get_model(self, name):
        return self.models[name]

    def getProtoClass(self, djangoClass):
        pClass = getattr(xos_pb2, djangoClass.__name__)
        return pClass

    def getPluralProtoClass(self, djangoClass):
        pClass = getattr(xos_pb2, djangoClass.plural_name)
        return pClass

    def convertFloat(self, x):
        if not x:
            return 0
        else:
            return float(x)

    def convertDateTime(self, x):
        if not x:
            return 0
        else:
            utc = pytz.utc
            return (x - datetime.datetime(1970, 1,
                                          1, tzinfo=utc)).total_seconds()
            # return time.mktime(x.timetuple())

    def convertForeignKey(self, x):
        if not x:
            return 0
        else:
            return int(x.id)

    def objToProto(self, obj):
        p_obj = self.getProtoClass(obj.__class__)()
        for field in obj._meta.fields:
            if getattr(obj, field.name) is None:
                continue

            ftype = field.get_internal_type()
            if (ftype == "CharField") or (
                    ftype == "TextField") or (ftype == "SlugField"):
                setattr(p_obj, field.name, str(getattr(obj, field.name)))
            elif (ftype == "BooleanField"):
                setattr(p_obj, field.name, getattr(obj, field.name))
            elif (ftype == "AutoField"):
                setattr(p_obj, field.name, int(getattr(obj, field.name)))
            elif (ftype == "IntegerField") or (ftype == "PositiveIntegerField") or (ftype == "BigIntegerField"):
                setattr(p_obj, field.name, int(getattr(obj, field.name)))
            elif (ftype == "ForeignKey"):
                setattr(
                    p_obj,
                    field.name + "_id",
                    self.convertForeignKey(
                        getattr(
                            obj,
                            field.name)))
            elif (ftype == "DateTimeField"):
                setattr(
                    p_obj,
                    field.name,
                    self.convertDateTime(
                        getattr(
                            obj,
                            field.name)))
            elif (ftype == "FloatField"):
                setattr(p_obj, field.name, float(getattr(obj, field.name)))
            elif (ftype == "GenericIPAddressField"):
                setattr(p_obj, field.name, str(getattr(obj, field.name)))

        for field in obj._meta.related_objects:
            related_name = field.related_name
            if not related_name:
                continue
            if "+" in related_name:
                continue
            try:
                rel_objs = getattr(obj, related_name)
            except Exception as e:
                # django makes catching this exception unnecessarily difficult
                if type(e).__name__ == "RelatedObjectDoesNotExist":
                    # OneToOneField throws this if relation does not exist
                    continue
                else:
                    raise

            if not hasattr(rel_objs, "all"):
                # this is in anticipation of OneToOneField causing problems
                continue

            for rel_obj in rel_objs.all():
                if not hasattr(p_obj, related_name + "_ids"):
                    continue
                getattr(p_obj, related_name + "_ids").append(rel_obj.id)

        # Generate a list of class names for the object. This includes its
        # ancestors. Anything that is a descendant of XOSBase or User
        # counts.

        bases = inspect.getmro(obj.__class__)
        bases = [
            x for x in bases if issubclass(
                x, XOSBase) or issubclass(
                x, User)]
        p_obj.class_names = ",".join([x.__name__ for x in bases])

        p_obj.self_content_type_id = obj.get_content_type_key()

        return p_obj

    def protoToArgs(self, djangoClass, message):
        args = {}
        fmap = {}
        fset = {}
        for field in djangoClass._meta.fields:
            fmap[field.name] = field
            if field.get_internal_type() == "ForeignKey":
                # foreign key can be represented as an id
                fmap[field.name + "_id"] = field

        for (fieldDesc, val) in message.ListFields():
            name = fieldDesc.name
            if name in fmap:
                if (name == "id"):
                    # don't let anyone set the id
                    continue
                ftype = fmap[name].get_internal_type()
                if (ftype == "CharField") or (
                        ftype == "TextField") or (ftype == "SlugField"):
                    args[name] = val
                elif (ftype == "BooleanField"):
                    args[name] = val
                elif (ftype == "AutoField"):
                    args[name] = val
                elif (ftype == "IntegerField") or (ftype == "PositiveIntegerField") or (ftype == "BigIntegerField"):
                    args[name] = val
                elif (ftype == "ForeignKey"):
                    if val == 0:  # assume object id 0 means None
                        args[name] = None
                    else:
                        # field name already has "_id" at the end
                        args[name] = val
                elif (ftype == "DateTimeField"):
                    utc = pytz.utc
                    args[name] = datetime.datetime.fromtimestamp(val, tz=utc)
                elif (ftype == "FloatField"):
                    args[name] = val
                elif (ftype == "GenericIPAddressField"):
                    args[name] = val
                fset[name] = True

        return args

    def querysetToProto(self, djangoClass, queryset):
        objs = queryset
        p_objs = self.getPluralProtoClass(djangoClass)()

        for obj in objs:
            new_obj = p_objs.items.add()
            new_obj.CopyFrom(self.objToProto(obj))

        return p_objs

    def get_live_or_deleted_object(self, djangoClass, id):
        """ Given an id, retrieve the object regardless of whether the object is live or deleted. """
        obj = None
        # First, check to see if the object has been deleted. Maybe the caller is
        # trying to update the policed timestamp of a deleted object.
        if hasattr(djangoClass, "deleted_objects"):
            deleted_objects = djangoClass.deleted_objects.filter(id=id)
            if deleted_objects:
                obj = deleted_objects[0]
        # No deleted object was found, so check for a live object.
        if not obj:
            obj = djangoClass.objects.get(id=id)
        return obj

    def xos_security_gate(self, obj, user, **access_types):
        sec_ctx = XOSDefaultSecurityContext()
        if not user:
            user = xos_anonymous_user

        sec_ctx.user = user

        for k, v in access_types.items():
            setattr(sec_ctx, k, v)

        obj_ctx = obj

        verdict, policy_name = obj.can_access(ctx=sec_ctx)

        # FIXME: This is the central point of enforcement for security policies
        #        Implement Auditing here.
        #        logging.info( ... )

        if not verdict:
            #    logging.critical( ... )
            if obj.id:
                object_descriptor = 'object %d' % obj.id
            else:
                object_descriptor = 'new object'

            raise XOSPermissionDenied(
                "User %(user_email)s cannot access %(django_class_name)s %(descriptor)s due to policy %(policy_name)s" % {
                    'user_email': user.email,
                    'django_class_name': obj.__class__.__name__,
                    'policy_name': policy_name,
                    'descriptor': object_descriptor})

    def xos_security_check(self, obj, user, **access_types):
        sec_ctx = XOSDefaultSecurityContext()
        if not user:
            user = xos_anonymous_user
        sec_ctx.user = user
        for k, v in access_types.items():
            setattr(sec_ctx, k, v)

        obj_ctx = obj

        verdict, _ = obj.can_access(ctx=sec_ctx)
        return verdict

    def get(self, djangoClass, user, id):
        obj = self.get_live_or_deleted_object(djangoClass, id)

        self.xos_security_gate(obj, user, read_access=True)

        return self.objToProto(obj)

    def create(self, djangoClass, user, request):
        args = self.protoToArgs(djangoClass, request)
        new_obj = djangoClass(**args)
        new_obj.caller = user

        self.xos_security_gate(new_obj, user, write_access=True)

        new_obj.save()
        return self.objToProto(new_obj)

    def update(self, djangoClass, user, id, message, context):
        obj = self.get_live_or_deleted_object(djangoClass, id)
        obj.caller = user

        self.xos_security_gate(obj, user, write_access=True)

        args = self.protoToArgs(djangoClass, message)
        for (k, v) in args.iteritems():
            setattr(obj, k, v)

        save_kwargs = {}
        for (k, v) in context.invocation_metadata():
            if k == "update_fields":
                save_kwargs["update_fields"] = v.split(",")
            elif k == "caller_kind":
                save_kwargs["caller_kind"] = v
            elif k == "always_update_timestamp":
                save_kwargs["always_update_timestamp"] = True

        obj.save(**save_kwargs)
        return self.objToProto(obj)

    def delete(self, djangoClass, user, id):
        obj = djangoClass.objects.get(id=id)

        self.xos_security_gate(obj, user, write_access=True)

        obj.delete()
        return Empty()

    def query_element_to_q(self, element):
        value = element.sValue
        if element.HasField("iValue"):
            value = element.iValue
        elif element.HasField("sValue"):
            value = element.sValue
        else:
            raise Exception("must specify iValue or sValue")

        if element.operator == element.EQUAL:
            q = Q(**{element.name: value})
        elif element.operator == element.LESS_THAN:
            q = Q(**{element.name + "__lt": value})
        elif element.operator == element.LESS_THAN_OR_EQUAL:
            q = Q(**{element.name + "__lte": value})
        elif element.operator == element.GREATER_THAN:
            q = Q(**{element.name + "__gt": value})
        elif element.operator == element.GREATER_THAN_OR_EQUAL:
            q = Q(**{element.name + "__gte": value})
        else:
            raise Exception("unknown operator")

        if element.invert:
            q = ~q

        return q

    def list(self, djangoClass, user):
        queryset = djangoClass.objects.all()
        filtered_queryset = (
            elt for elt in queryset if self.xos_security_check(
                elt, user, read_access=True))

        # FIXME: Implement auditing here
        # logging.info("User requested x objects, y objects were filtered out by policy z")

        return self.querysetToProto(djangoClass, filtered_queryset)

    def filter(self, djangoClass, user, request):
        query = None
        if request.kind == request.DEFAULT:
            for element in request.elements:
                if query:
                    query = query & self.query_element_to_q(element)
                else:
                    query = self.query_element_to_q(element)
            queryset = djangoClass.objects.filter(query)
        elif request.kind == request.SYNCHRONIZER_DIRTY_OBJECTS:
            query = (Q(enacted__lt=F('updated')) | Q(enacted=None)) & Q(
                lazy_blocked=False) & Q(no_sync=False)
            queryset = djangoClass.objects.filter(query)
        elif request.kind == request.SYNCHRONIZER_DELETED_OBJECTS:
            queryset = djangoClass.deleted_objects.all()
        elif request.kind == request.SYNCHRONIZER_DIRTY_POLICIES:
            query = (Q(policed__lt=F('updated')) | Q(
                policed=None)) & Q(no_policy=False)
            queryset = djangoClass.objects.filter(query)
        elif request.kind == request.SYNCHRONIZER_DELETED_POLICIES:
            query = Q(policed__lt=F('updated')) | Q(policed=None)
            queryset = djangoClass.deleted_objects.filter(query)
        elif request.kind == request.ALL:
            queryset = djangoClass.objects.all()

        filtered_queryset = (
            elt for elt in queryset if self.xos_security_check(
                elt, user, read_access=True))

        # FIXME: Implement auditing here
        # logging.info("User requested x objects, y objects were filtered out by policy z")

        return self.querysetToProto(djangoClass, filtered_queryset)

    def authenticate(self, context, required=False):
        for (k, v) in context.invocation_metadata():
            if (k.lower() == "authorization"):
                (method, auth) = v.split(" ", 1)
                if (method.lower() == "basic"):
                    auth = base64.b64decode(auth)
                    (username, password) = auth.split(":")
                    user = cached_authenticator.authenticate(
                        username=username, password=password)
                    if not user:
                        raise XOSPermissionDenied(
                            "failed to authenticate %s:%s" %
                            (username, password))
                    return user
            elif (k.lower() == "x-xossession"):
                s = SessionStore(session_key=v)
                id = s.get("_auth_user_id", None)
                if not id:
                    raise XOSPermissionDenied(
                        "failed to authenticate token %s" % v)
                user = User.objects.get(id=id)
                print "authenticated sessionid %s as %s" % (v, user)
                return user

        if required:
            raise XOSPermissionDenied("This API requires authentication")

        return None
