from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework.views import APIView
from core.models import *
from django.forms import widgets
from django.core.exceptions import PermissionDenied
from xos.exceptions import XOSNotFound

class SSHKeyList(APIView):
    method_kind = "list"
    method_name = "sshkeys"

    def get(self, request, format=None):
        instances=[]
        for instance in self.get_queryset().all():
            if instance.instance_id:
                instances.append( {"id": instance.instance_id,
                                   "public_keys": instance.get_public_keys(),
                                   "node_name": instance.node.name } )

        return Response(instances)

    def get_queryset(self):
        queryset = queryset=Instance.objects.all()

        node_name = self.request.query_params.get('node_name', None)
        if node_name is not None:
            queryset = queryset.filter(node__name = node_name)

        return queryset

class SSHKeyDetail(APIView):
    method_kind = "detail"
    method_name = "sshkeys"

    def get(self, request, format=None, pk=0):
        instances = self.get_queryset().filter(instance_id=pk)
        if not instances:
            raise XOSNotFound("didn't find instance for instance %s" % pk)
        return Response( [ {"id": instances[0].instance_id,
                            "public_keys": instances[0].get_public_keys(),
                            "node_name": instances[0].node.name } ])

    def get_queryset(self):
        queryset = queryset=Instance.objects.all()

        node_name = self.request.query_params.get('node_name', None)
        if node_name is not None:
            queryset = queryset.filter(node__name = node_name)

        return queryset

