from core.serializers import NodeSerializer
from rest_framework import generics
from core.models import Node

class NodeList(generics.ListCreateAPIView):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer

class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer


