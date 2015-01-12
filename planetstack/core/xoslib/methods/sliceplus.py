from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from core.models import *
from django.forms import widgets
from core.xoslib.objects.sliceplus import SlicePlus
from plus import PlusSerializerMixin, PlusRetrieveUpdateDestroyAPIView, PlusListCreateAPIView

if hasattr(serializers, "ReadOnlyField"):
    # rest_framework 3.x
    IdField = serializers.ReadOnlyField
else:
    # rest_framework 2.x
    IdField = serializers.Field

class NetworkPortsField(serializers.WritableField):   # note: maybe just Field in rest_framework 3.x instead of WritableField
    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        return data

class SiteAllocationField(serializers.WritableField):   # note: maybe just Field in rest_framework 3.x instead of WritableField
    def to_representation(self, obj):
        return json.dumps(obj)

    def to_internal_value(self, data):
        return json.loads(data)

class SlicePlusIdSerializer(serializers.ModelSerializer, PlusSerializerMixin):
        id = IdField()

        sliceInfo = serializers.SerializerMethodField("getSliceInfo")
        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
        network_ports = NetworkPortsField(required=False)
        site_allocation = SiteAllocationField(required=False)

        def getSliceInfo(self, slice):
            return slice.getSliceInfo(user=self.context['request'].user)

        def getHumanReadableName(self, obj):
            return str(obj)

        networks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
#        availableNetworks = serializers.PrimaryKeyRelatedField(many=True, read_only=True, view_name='network-detail')

        class Meta:
            model = SlicePlus
            fields = ('humanReadableName', 'id','created','updated','enacted','name','enabled','omf_friendly','description','slice_url','site','max_slivers','image_preference','service','network','mount_data_sets',
                      'serviceClass','creator','networks','sliceInfo','network_ports','backendIcon','backendHtml','site_allocation')

class SlicePlusList(PlusListCreateAPIView): #generics.ListCreateAPIView):
    queryset = SlicePlus.objects.select_related().all()
    serializer_class = SlicePlusIdSerializer

    method_kind = "list"
    method_name = "slicesplus"

    def get_queryset(self):
        return SlicePlus.select_by_user(self.request.user)

class SlicePlusDetail(PlusRetrieveUpdateDestroyAPIView):
    queryset = SlicePlus.objects.select_related().all()
    serializer_class = SlicePlusIdSerializer

    method_kind = "detail"
    method_name = "slicesplus"

    def get_queryset(self):
        return SlicePlus.select_by_user(self.request.user)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SlicePlusDetail, self).update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_update(request.user):
            return super(SlicePlusDetail, self).destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
