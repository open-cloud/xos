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

class SSHKeysSerializer(PlusModelSerializer):
    id = serializers.CharField(read_only=True, source="instance_id")
    public_keys = serializers.ListField(read_only=True, source="get_public_keys")
    node_name = serializers.CharField(read_only=True, source="node.name")

    class Meta:
        model = Instance
        fields = ('id', 'public_keys', 'node_name')

class SSHKeysViewSet(XOSViewSet):
    base_name = "sshkeys"
    method_name = "sshkeys"
    method_kind = "viewset"
    serializer_class = SSHKeysSerializer
    read_only = True

    lookup_field = "instance_id"
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        queryset = queryset=Instance.objects.exclude(Q(instance_id__isnull=True) | Q(instance_id__exact=''))

        node_name = self.request.query_params.get('node_name', None)
        if node_name is not None:
            queryset = queryset.filter(node__name = node_name)

        return queryset


