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

class OnboardingViewSet(XOSViewSet):
    base_name = "onboarding"
    method_name = "onboarding"
    method_kind = "viewset"

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = [] #super(CordSubscriberViewSet, self).get_urlpatterns(api_path=api_path)

        patterns.append( self.list_url("xos/ready/$", {"get": "get_xos_ready"}, "xos_ready") )
        patterns.append( self.list_url("xos/rebuild/$", {"post": "post_rebuild"}, "xos_rebuild") )

        patterns.append( self.list_url("summary/$", {"get": "get_summary"}, "summary") )

        patterns.append( self.list_url("services/$", {"get": "get_service_list"}, "service_list") )
        patterns.append( self.list_url("services/(?P<service>[a-zA-Z0-9\-_]+)/ready/$", {"get": "get_service_ready"}, "service_ready") )


        return patterns

    def is_ready(self, obj):
        return (obj.enacted is not None) and (obj.updated is not None) and (obj.enacted>=obj.updated) and (obj.backend_status.startswith("1"))

    def get_xos_ready(self, request):
        xos = XOS.objects.all()
        if not xos:
            return Response(false)

        xos=xos[0]

        result = (xos.enacted is not None) and (xos.updated is not None) and (xos.enacted>=xos.updated) and (xos.backend_status.startswith("1"))
        return HttpResponse( json.dumps(result), content_type="application/javascript" )

    def post_rebuild(self, request):
        xos = XOS.objects.all()
        if not xos:
            raise Exception("There is no XOS object")

        xos=xos[0]

        xos.rebuild()

        return Response(True)

    def get_summary(self, request):
        result = []

        xos = XOS.objects.all()
        if not xos:
            result.append( ("XOS", false) )
        else:
            xos=xos[0]

            result.append( ("XOS", self.is_ready(xos)) )

            for sc in xos.service_controllers.all():
                result.append( (sc.name, self.is_ready(sc)) )

        result = "\n".join( ["%s: %s" % (x[0], x[1]) for x in result] )
        if result:
            result = result + "\n"

        return HttpResponse( result, content_type="text/ascii" )

    def get_service_list(self, request):
        xos = XOS.objects.all()
        if not xos:
            return Response([])

        xos=xos[0]

        result = []
        for sc in xos.service_controllers.all():
            result.append(sc.name)

        return HttpResponse( json.dumps(result), content_type="application/javascript")

    def get_service_ready(self, request, service):
        xos = XOS.objects.all()
        if not xos:
            return Response([])

        xos=xos[0]

        sc=xos.service_controllers.filter(name=service)
        if not sc:
            return HttpResponse("Not Found", status_code=404)

        sc=sc[0]
        result = self.is_ready(sc)

        return HttpResponse( json.dumps(result), content_type="application/javascript")





