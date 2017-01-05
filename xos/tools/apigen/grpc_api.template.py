import time
from protos import xos_pb2

from core.models import *

class XosService(xos_pb2.xosServicer):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool

    def stop(self):
        pass

    def getProtoClass(self, djangoClass):
        pClass = getattr(xos_pb2, djangoClass.__name__)
        return pClass

    def getPluralProtoClass(self, djangoClass):
        pClass = getattr(xos_pb2, djangoClass.__name__ + "s")
        return pClass

    def convertString(self, x):
        if not x:
            return ""
        else:
            return str(x)

    def convertInt(self, x):
        if not x:
            return 0
        else:
            return int(x)

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
            if (field.get_internal_type() == "CharField") or (field.get_internal_type() == "TextField") or (field.get_internal_type() == "SlugField"):
                setattr(p_obj, field.name, self.convertString(getattr(obj, field.name)))
            elif (field.get_internal_type() == "BooleanField"):
                setattr(p_obj, field.name, getattr(obj, field.name))
            elif (field.get_internal_type() == "AutoField"):
                setattr(p_obj, field.name, self.convertInt(getattr(obj, field.name)))
            elif (field.get_internal_type() == "IntegerField") or (field.get_internal_type() == "PositiveIntegerField"):
                setattr(p_obj, field.name, self.convertInt(getattr(obj, field.name)))
            elif (field.get_internal_type() == "ForeignKey"):
                setattr(p_obj, field.name+"_id", self.convertForeignKey(getattr(obj, field.name)))
            elif (field.get_internal_type() == "DateTimeField"):
                setattr(p_obj, field.name, self.convertDateTime(getattr(obj, field.name)))
            elif (field.get_internal_type() == "FloatField"):
                setattr(p_obj, field.name, self.convertFloat(getattr(obj, field.name)))
            elif (field.get_internal_type() == "GenericIPAddressField"):
                setattr(p_obj, field.name, self.convertString(getattr(obj, field.name)))
        return p_obj

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

{% for object in generator.all() %}
    def List{{ object.camel() }}(self, request, context):
      return self.querysetToProto({{ object.camel() }}, {{ object.camel() }}.objects.all())

    def Get{{ object.camel() }}(self, request, context):
      return self.get({{ object.camel() }}, request.id)
{% endfor %}


