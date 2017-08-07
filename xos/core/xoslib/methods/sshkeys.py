
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

