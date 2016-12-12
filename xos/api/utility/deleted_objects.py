import json
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField
from django.db import models

class DeletedObjectsViewSet(XOSViewSet):
    base_name = "deleted_objects"
    method_name = "deleted_objects"
    method_kind = "viewset"

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = []

        patterns.append( self.list_url("$", {"get": "get_deleted_objects"}, "list_deleted_objects") )

        return patterns

    def get_deleted_objects(self, request):
        deleted_models = []
        for model in models.get_models(include_auto_created=False):
            if hasattr(model, "deleted_objects"):
                if hasattr(model,"_meta") and hasattr(model._meta,"proxy") and model._meta.proxy:
                    # ignore proxy models; we'll just report the base
                    continue
                for obj in model.deleted_objects.all():
                    deleted_models.append( {"classname": obj.__class__.__name__,
                                            "unicode": str(obj),
                                            "id": obj.id} )

        return HttpResponse( json.dumps(deleted_models), content_type="application/javascript")





