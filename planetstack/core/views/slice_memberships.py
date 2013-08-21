from core.serializers import SliceMembershipSerializer
from rest_framework import generics
from core.models import SliceMembership

class SliceMembershipList(generics.ListCreateAPIView):
    queryset = SliceMembership.objects.all()
    serializer_class = SliceMembershipSerializer

class SliceMembershipDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SliceMembership.objects.all()
    serializer_class = SliceMembershipSerializer


