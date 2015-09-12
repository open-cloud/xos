from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from core.models import *
from django.forms import widgets
from core.xoslib.objects.sliceplus import SlicePlus
from plus import PlusSerializerMixin
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied

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

class DictionaryField(serializers.WritableField):   # note: maybe just Field in rest_framework 3.x instead of WritableField
    def to_representation(self, obj):
        return json.dumps(obj)

    def to_internal_value(self, data):
        return json.loads(data)

class ListField(serializers.WritableField):   # note: maybe just Field in rest_framework 3.x instead of WritableField
    def to_representation(self, obj):
        return json.dumps(obj)

    def to_internal_value(self, data):
        return json.loads(data)

class SlicePlusIdSerializer(serializers.ModelSerializer, PlusSerializerMixin):
        id = IdField()

        sliceInfo = serializers.SerializerMethodField("getSliceInfo")
        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
        network_ports = NetworkPortsField(required=False)
        site_allocation = DictionaryField(required=False)
        site_ready = DictionaryField(required=False)
        users = ListField(required=False)
        user_names = ListField(required=False) # readonly = True ?
        current_user_can_see = serializers.SerializerMethodField("getCurrentUserCanSee")

        def getCurrentUserCanSee(self, slice):
            # user can 'see' the slice if he is the creator or he has a role
            current_user = self.context['request'].user
            if (slice.creator and slice.creator==current_user):
                return True;
            return (len(slice.getSliceInfo(current_user)["roles"]) > 0)

        def getSliceInfo(self, slice):
            return slice.getSliceInfo(user=self.context['request'].user)

        def getHumanReadableName(self, obj):
            return str(obj)

        networks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

        class Meta:
            model = SlicePlus
            fields = ('humanReadableName', 'id','created','updated','enacted','name','enabled','omf_friendly','description','slice_url','site','max_instances','service','network','mount_data_sets',
                      'default_image', 'default_flavor',
                      'serviceClass','creator','networks','sliceInfo','network_ports','backendIcon','backendHtml','site_allocation','site_ready','users',"user_names","current_user_can_see")

class SlicePlusList(XOSListCreateAPIView):
    queryset = SlicePlus.objects.select_related().all()
    serializer_class = SlicePlusIdSerializer

    method_kind = "list"
    method_name = "slicesplus"

    def get_queryset(self):
        current_user_can_see = self.request.QUERY_PARAMS.get('current_user_can_see', False)

        if (not self.request.user.is_authenticated()):
            raise XOSPermissionDenied("You must be authenticated in order to use this API")

        slices = SlicePlus.select_by_user(self.request.user)

        # If current_user_can_see is set, then filter the queryset to return
        # only those slices that the user is either creator or has privilege
        # on.
        if (current_user_can_see):
            slice_ids = []
            for slice in slices:
                if (self.request.user == slice.creator) or (len(slice.getSliceInfo(self.request.user)["roles"]) > 0):
                    slice_ids.append(slice.id)

            slices = SlicePlus.objects.filter(id__in=slice_ids)

        return slices

class SlicePlusDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = SlicePlus.objects.select_related().all()
    serializer_class = SlicePlusIdSerializer

    method_kind = "detail"
    method_name = "slicesplus"

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSPermissionDenied("You must be authenticated in order to use this API")
        return SlicePlus.select_by_user(self.request.user)


