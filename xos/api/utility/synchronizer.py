
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework.exceptions import APIException
from core.models import *
from django.forms import widgets
from core.xoslib.objects.sliceplus import SlicePlus
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
import json
from core.models import Slice, SlicePrivilege, SliceRole, Instance, Site, Node, User
from operator import itemgetter, attrgetter
from api.xosapi_helpers import PlusObjectMixin, PlusModelSerializer

IdField = serializers.ReadOnlyField


class SynchronizerSerializer(PlusModelSerializer):
    id = IdField()

    name = serializers.CharField(required=False)

    class Meta:
        model = Diag
        fields = ('id', 'name', 'backend_status', 'backend_register')


class SynchronizerList(XOSListCreateAPIView):
    queryset = Diag.objects.all()
    serializer_class = SynchronizerSerializer

    method_kind = "list"
    method_name = "synchronizer"

    def get_queryset(self):
        name = self.request.query_params.get('name', False)

        if (not self.request.user.is_authenticated()):
            raise XOSPermissionDenied("You must be authenticated in order to use this API")
        if(name):
            return Diag.objects.filter(name=name)
        return Diag.objects.all()


class SynchronizerDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = Diag.objects.all()
    serializer_class = SynchronizerSerializer

    method_kind = "detail"
    method_name = "synchronizer"

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSPermissionDenied("You must be authenticated in order to use this API")

        print "kwargs"
        print self.request
        print self.kwargs['pk']

        return Diag.objects.filter(id=self.kwargs['pk'])
