from core.serializers import SitePrivilegeSerializer
from rest_framework import generics
from core.models import SitePrivilege

class SitePrivilegeList(generics.ListCreateAPIView):
    queryset = SitePrivilege.objects.all()
    serializer_class = SitePrivilegeSerializer

class SitePrivilegeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SitePrivilege.objects.all()
    serializer_class = SitePrivilegeSerializer


