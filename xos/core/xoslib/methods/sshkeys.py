from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework.views import APIView
from core.models import *
from django.forms import widgets
from syndicate_storage.models import Volume
from django.core.exceptions import PermissionDenied
from xos.exceptions import XOSNotFound

class SSHKeyList(APIView):
    method_kind = "list"
    method_name = "sshkeys"

    def get(self, request, format=None):
        instances=[]
        for sliver in self.get_queryset().all():
            if sliver.instance_id:
                instances.append( {"id": sliver.instance_id,
                                   "public_keys": sliver.get_public_keys(),
                                   "node_name": sliver.node.name } )

        return Response(instances)

    def get_queryset(self):
        queryset = queryset=Sliver.objects.all()

        node_name = self.request.QUERY_PARAMS.get('node_name', None)
        if node_name is not None:
            queryset = queryset.filter(node__name = node_name)

        return queryset

class SSHKeyDetail(APIView):
    method_kind = "detail"
    method_name = "sshkeys"

    def get(self, request, format=None, pk=0):
        slivers = self.get_queryset().filter(instance_id=pk)
        if not slivers:
            raise XOSNotFound("didn't find sliver for instance %s" % pk)
        return Response( [ {"id": slivers[0].instance_id,
                            "public_keys": slivers[0].get_public_keys(),
                            "node_name": slivers[0].node.name } ])

    def get_queryset(self):
        queryset = queryset=Sliver.objects.all()

        node_name = self.request.QUERY_PARAMS.get('node_name', None)
        if node_name is not None:
            queryset = queryset.filter(node__name = node_name)

        return queryset

