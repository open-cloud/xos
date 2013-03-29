# Create your views here.

from plstackapi.core.models import Site
from serializers import *
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'nodes': reverse('node-list', request=request, format=format),
        'sites': reverse('site-list', request=request, format=format),
        'deploymentNetworks': reverse('deploymentnetwork-list', request=request, format=format),
        'slices': reverse('slice-list', request=request, format=format)
    })
  
class SiteList(generics.ListCreateAPIView):
    model=Site
    serializer_class = SiteSerializer

class SiteDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Site
    serializer_class = SiteSerializer

class SliceList(generics.ListCreateAPIView):
    model=Slice
    serializer_class = SliceSerializer

class SliceDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Slice
    serializer_class = SliceSerializer

class NodeList(generics.ListCreateAPIView):
    model=Node
    serializer_class = NodeSerializer

class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Node
    serializer_class = NodeSerializer

class SliverList(generics.ListCreateAPIView):
    model=Sliver
    serializer_class = SliverSerializer

class SliverDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Sliver
    serializer_class = SliverSerializer

class DeploymentNetworkList(generics.ListCreateAPIView):
    model=DeploymentNetwork
    serializer_class = DeploymentNetworkSerializer

class DeploymentNetworkDetail(generics.RetrieveUpdateDestroyAPIView):
    model = DeploymentNetwork
    serializer_class = DeploymentNetworkSerializer

class SiteDeploymentNetworkList(generics.ListCreateAPIView):
    model=SiteDeploymentNetwork
    serializer_class = SiteDeploymentNetworkSerializer

class SiteDeploymentNetworkDetail(generics.RetrieveUpdateDestroyAPIView):
    model = SiteDeploymentNetwork
    serializer_class = DeploymentNetworkSerializer
