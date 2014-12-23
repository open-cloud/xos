from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from core.models import *
from django.forms import widgets
from core.xoslib.objects.sliceplus import SlicePlus
from plus import PlusSerializerMixin

class SlicePlusIdSerializer(serializers.ModelSerializer, PlusSerializerMixin):
        id = serializers.ReadOnlyField()

        sliceInfo = serializers.SerializerMethodField("getSliceInfo")
        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        def getSliceInfo(self, slice):
            return slice.getSliceInfo(user=self.context['request'].user)

        def getHumanReadableName(self, obj):
            return str(obj)

        networks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')
        availableNetworks = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='network-detail')

        class Meta:
            model = SlicePlus
            fields = ('humanReadableName', 'id','created','updated','enacted','name','enabled','omf_friendly','description','slice_url','site','max_slivers','imagePreference','service','network','mountDataSets','serviceClass','creator','networks','availableNetworks','sliceInfo','backendIcon','backendHtml')

class SlicePlusList(generics.ListCreateAPIView):
    queryset = SlicePlus.objects.select_related().all()
    serializer_class = SlicePlusIdSerializer

    method_kind = "list"
    method_name = "slicesplus"

    def get_queryset(self):
        return SlicePlus.select_by_user(self.request.user)

    def create(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.caller = request.user
        if obj.can_update(request.user):
            return super(SliceList, self).create(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SlicePlusDetail(generics.RetrieveUpdateDestroyAPIView):
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
