from core.serializers import RoleSerializer
from rest_framework import generics
from core.models import Role

class RoleList(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class RoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


