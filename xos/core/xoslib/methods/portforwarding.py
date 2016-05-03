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

class PortForwardingList(APIView):
    method_kind = "list"
    method_name = "portforwarding"

    def get(self, request, format=None):
        ports=[]
        for port in self.get_queryset().all():
            if port.network and port.network.ports and port.instance and port.instance.node and port.ip:
                ports.append( {"id": port.id,
                               "ip": port.ip,
                               "ports": port.network.ports,
                               "hostname": port.instance.node.name} )

        return Response(ports)

    def get_queryset(self):
        queryset = queryset=Port.objects.all()

        node_name = self.request.query_params.get('node_name', None)
        if node_name is not None:
            queryset = queryset.filter(instance__node__name = node_name)

        return queryset

class PortForwardingDetail(APIView):
    method_kind = "detail"
    method_name = "portforwarding"

    def get(self, request, format=None, pk=0):
        ports = self.get_queryset().filter(id=pk)
        if not ports:
            raise XOSNotFound("didn't find port for port_id %s" % pk)

        port = ports[0]
        return Response( {"id": port.id,
                          "ip": port.ip,
                          "ports": port.network.ports,
                          "hostname": port.instance.node.name} )

    def get_queryset(self):
        queryset = queryset=Port.objects.all()

        node_name = self.request.query_params.get('node_name', None)
        if node_name is not None:
            queryset = queryset.filter(instance__node__name = node_name)

        return queryset

