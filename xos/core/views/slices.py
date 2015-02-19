from core.serializers import SliceSerializer
from rest_framework import generics
from core.models import Slice

class SliceList(generics.ListCreateAPIView):
    queryset = Slice.objects.all()
    serializer_class = SliceSerializer

class SliceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Slice.objects.all()
    serializer_class = SliceSerializer


