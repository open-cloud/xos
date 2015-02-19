from core.serializers import SliverSerializer
from rest_framework import generics
from core.models import Sliver

class SliverList(generics.ListCreateAPIView):
    queryset = Sliver.objects.all()
    serializer_class = SliverSerializer

class SliverDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sliver.objects.all()
    serializer_class = SliverSerializer


