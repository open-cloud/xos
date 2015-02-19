from core.serializers import SlicePrivilegeSerializer
from rest_framework import generics
from core.models import SlicePrivilege

class SlicePrivilegeList(generics.ListCreateAPIView):
    queryset = SlicePrivilege.objects.all()
    serializer_class = SlicePrivilegeSerializer

class SlicePrivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SlicePrivilege.objects.all()
    serializer_class = SlicePrivilegeSerializer


