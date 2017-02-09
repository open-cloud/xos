import base64
import time
from protos import xos_pb2
from google.protobuf.empty_pb2 import Empty

from django.contrib.auth import authenticate as django_authenticate
from core.models import *
from xos.exceptions import *

from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

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
        pClass = getattr(xos_pb2, djangoClass.__name__ + "s")
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
            return time.mktime(x.timetuple())

    def convertForeignKey(self, x):
        if not x:
            return 0
        else:
            return int(x.id)

    def objToProto(self, obj):
        p_obj = self.getProtoClass(obj.__class__)()
        for field in obj._meta.fields:
            if getattr(obj, field.name) == None:
                continue

            ftype = field.get_internal_type()
            if (ftype == "CharField") or (ftype == "TextField") or (ftype == "SlugField"):
                setattr(p_obj, field.name, str(getattr(obj, field.name)))
            elif (ftype == "BooleanField"):
                setattr(p_obj, field.name, getattr(obj, field.name))
            elif (ftype == "AutoField"):
                setattr(p_obj, field.name, int(getattr(obj, field.name)))
            elif (ftype == "IntegerField") or (ftype == "PositiveIntegerField"):
                setattr(p_obj, field.name, int(getattr(obj, field.name)))
            elif (ftype == "ForeignKey"):
                setattr(p_obj, field.name+"_id", self.convertForeignKey(getattr(obj, field.name)))
            elif (ftype == "DateTimeField"):
                setattr(p_obj, field.name, self.convertDateTime(getattr(obj, field.name)))
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
            rel_objs = getattr(obj, related_name)
            for rel_obj in rel_objs.all():
                if not hasattr(p_obj,related_name+"_ids"):
                    continue
                x=getattr(p_obj,related_name+"_ids").append(rel_obj.id)

        return p_obj

    def protoToArgs(self, djangoClass, message):
        args={}
        fmap={}
        fset={}
        for field in djangoClass._meta.fields:
            fmap[field.name] = field
            if field.get_internal_type() == "ForeignKey":
               # foreign key can be represented as an id
               fmap[field.name + "_id"] = field

        for (fieldDesc, val) in message.ListFields():
            name = fieldDesc.name
            if name in fmap:
                if (name=="id"):
                    # don't let anyone set the id
                    continue
                ftype = fmap[name].get_internal_type()
                if (ftype == "CharField") or (ftype == "TextField") or (ftype == "SlugField"):
                    args[name] = val
                elif (ftype == "BooleanField"):
                    args[name] = val
                elif (ftype == "AutoField"):
                    args[name] = val
                elif (ftype == "IntegerField") or (ftype == "PositiveIntegerField"):
                    args[name] = val
                elif (ftype == "ForeignKey"):
                    args[name] = val # field name already has "_id" at the end
                elif (ftype == "DateTimeField"):
                    pass # do something special here
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

    def get(self, djangoClass, id):
        obj = djangoClass.objects.get(id=id)
        return self.objToProto(obj)

    def create(self, djangoClass, user, request):
        args = self.protoToArgs(djangoClass, request)
        new_obj = djangoClass(**args)
        new_obj.caller = user
        if (not user) or (not new_obj.can_update(user)):
            raise XOSPermissionDenied()
        new_obj.save()
        return self.objToProto(new_obj)

    def update(self, djangoClass, user, id, message):
        obj = djangoClass.objects.get(id=id)
        obj.caller = user
        if (not user) or (not obj.can_update(user)):
            raise XOSPermissionDenied()
        args = self.protoToArgs(djangoClass, message)
        for (k,v) in args.iteritems():
            setattr(obj, k, v)
        obj.save()
        return self.objToProto(obj)

    def delete(self, djangoClass, user, id):
      obj = djangoClass.objects.get(id=id)
      if (not user) or (not obj.can_update(user)):
          raise XOSPermissionDenied()
      obj.delete()
      return Empty()

    def authenticate(self, context):
        for (k, v) in context.invocation_metadata():
            if (k.lower()=="authorization"):
                (method, auth) = v.split(" ",1)
                if (method.lower() == "basic"):
                    auth = base64.b64decode(auth)
                    (username, password) = auth.split(":")
                    user = django_authenticate(username=username, password=password)
                    if not user:
                        raise XOSPermissionDenied("failed to authenticate %s:%s" % (username, password))
                    print "authenticated %s:%s as %s" % (username, password, user)
                    return user
            elif (k.lower()=="x-xossession"):
                 s = SessionStore(session_key=v)
                 id = s.get("_auth_user_id", None)
                 if not id:
                     raise XOSPermissionDenied("failed to authenticate token %s" % v)
                 user = User.objects.get(id=id)
                 print "authenticated sessionid %s as %s" % (v, user)
                 return user


        return None

