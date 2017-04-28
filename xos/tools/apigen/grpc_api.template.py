import base64
import time
from protos import xos_pb2
from google.protobuf.empty_pb2 import Empty

from django.contrib.auth import authenticate as django_authenticate
from xos.exceptions import *
from apihelper import XOSAPIHelperMixin, translate_exceptions

class XosService(xos_pb2.xosServicer, XOSAPIHelperMixin):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool
        XOSAPIHelperMixin.__init__(self)

    def stop(self):
        pass

{% for object in generator.all() %}
    @translate_exceptions
    def List{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      model=self.get_model("{{ object.camel() }}")
      return self.querysetToProto(model, model.objects.all())

    @translate_exceptions
    def Filter{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      model=self.get_model("{{ object.camel() }}")
      return self.filter(model, request)

    @translate_exceptions
    def Get{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      model=self.get_model("{{ object.camel() }}")
      return self.get(model, request.id)

    @translate_exceptions
    def Create{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      model=self.get_model("{{ object.camel() }}")
      return self.create(model, user, request)

    @translate_exceptions
    def Delete{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      model=self.get_model("{{ object.camel() }}")
      return self.delete(model, user, request.id)

    @translate_exceptions
    def Update{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      model=self.get_model("{{ object.camel() }}")
      return self.update(model, user, request.id, request, context)

{% endfor %}


