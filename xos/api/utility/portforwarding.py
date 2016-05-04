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
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField
from django.db.models import Q

class PortForwardingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    ip = serializers.CharField(read_only=True)
    ports = serializers.CharField(read_only=True, source="network.ports")
    hostname = serializers.CharField(read_only=True, source="instance.node.name")

    class Meta:
        model = Port
        fields = ('id', 'ip', 'ports', 'hostname')

class PortForwardingViewSet(XOSViewSet):
    base_name = "portforwarding"
    method_name = "portforwarding"
    method_kind = "viewset"
    serializer_class = PortForwardingSerializer

    def get_queryset(self):
        queryset=Port.objects.exclude(Q(network__isnull=True) |
                                                  Q(instance__isnull=True) |
                                                  Q(instance__node__isnull=True) |
                                                  Q(network__ports__isnull=True) | Q(network__ports__exact='') |
                                                  Q(ip__isnull=True))

        node_name = self.request.query_params.get('node_name', None)
        if node_name is not None:
            queryset = queryset.filter(instance__node__name = node_name)

        if "" in [q.ip for q in list(queryset)]:
            # Q(ip__exact=='') does not work right, so let's filter the hard way
            queryset = [q for q in list(queryset) if q.ip!='']
            queryset = [q.id for q in queryset]
            queryset = Port.objects.filter(pk__in=queryset)

        return queryset


