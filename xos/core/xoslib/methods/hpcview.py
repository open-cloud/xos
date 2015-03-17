from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework.views import APIView
from core.models import *
from hpc.models import *
from requestrouter.models import *
from django.forms import widgets
from syndicate_storage.models import Volume
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
import time

# This REST API endpoint contains a bunch of misc information that the
# tenant view needs to display

def get_service_slices(service):
    try:
        return service.slices.all()
    except:
        return service.service.all()

def lookup_tag(service, sliver, name, default=None):
    sliver_type = ContentType.objects.get_for_model(sliver)
    t = Tag.objects.filter(service=service, name=name, content_type__pk=sliver_type.id, object_id=sliver.id)
    if t:
        return t[0].value
    else:
        return default

def lookup_time(service, sliver, name):
    v = lookup_tag(service, sliver, name)
    if v:
        return str(time.time() - float(v))
    else:
        return None

def getHpcDict(user, pk):
    hpc = HpcService.objects.get(pk=pk)
    slices = get_service_slices(hpc)

    dnsdemux_slice = None
    for slice in slices:
        if "dnsdemux" in slice.name:
            dnsdemux_service = hpc
            dnsdemux_slice = slice

    if not dnsdemux_slice:
        rr = RequestRouterService.objects.all()
        if rr:
            rr=rr[0]
            slices = get_service_slices(rr)
            for slice in slices:
                if "dnsdemux" in slice.name:
                    dnsdemux_service = rr
                    dnsdemux_slice = slice

    dnsdemux=[]
    for sliver in dnsdemux_slice.slivers.all():
        dnsdemux.append( {"name": sliver.node.name,
                       "watcher.DNS.msg": lookup_tag(dnsdemux_service, sliver, "watcher.DNS.msg"),
                       "watcher.DNS.time": lookup_time(dnsdemux_service, sliver, "watcher.DNS.time"),
                       "ip": sliver.get_public_ip() })

    return { "dnsdemux": dnsdemux }


class HpcList(APIView):
    method_kind = "list"
    method_name = "hpcview"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        results = []
        for hpc in HpcService.objects.all():
            results.append(getHpcDict(request.user, hpc.pk))
        return Response( results )

class HpcDetail(APIView):
    method_kind = "detail"
    method_name = "hpcview"

    def get(self, request, format=None, pk=0):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        return Response( [getHpcViewDict(request.user, pk)] )

