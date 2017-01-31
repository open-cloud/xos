import base64
import time
from protos import xos_pb2
from google.protobuf.empty_pb2 import Empty

from django.contrib.auth import authenticate as django_authenticate
from core.models import *
from xos.exceptions import *
from apihelper import XOSAPIHelperMixin

class XosService(xos_pb2.xosServicer, XOSAPIHelperMixin):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool

    def stop(self):
        pass

{% for object in generator.all() %}
    def List{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      return self.querysetToProto({{ object.camel() }}, {{ object.camel() }}.objects.all())

    def Get{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      return self.get({{ object.camel() }}, request.id)

    def Create{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      return self.create({{ object.camel() }}, user, request)

    def Delete{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      return self.delete({{ object.camel() }}, user, request.id)

    def Update{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      return self.update({{ object.camel() }}, user, request.id, request)

{% endfor %}


