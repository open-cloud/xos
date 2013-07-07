from core.serializers import ServiceResourceSerializer
from rest_framework import generics
from core.models import ServiceResource

class ServiceResourceList(generics.ListCreateAPIView):
    queryset = ServiceResource.objects.all()
    serializer_class = ServiceResourceSerializer

class ServiceResourceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceResource.objects.all()
    serializer_class = ServiceResourceSerializer


