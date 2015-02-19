from core.serializers import ServiceClassSerializer
from rest_framework import generics
from core.models import ServiceClass

class ServiceClassList(generics.ListCreateAPIView):
    queryset = ServiceClass.objects.all()
    serializer_class = ServiceClassSerializer

class ServiceClassDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceClass.objects.all()
    serializer_class = ServiceClassSerializer


