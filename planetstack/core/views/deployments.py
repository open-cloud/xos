from core.serializers import DeploymentSerializer
from rest_framework import generics
from core.models import Deployment

class DeploymentList(generics.ListCreateAPIView):
    queryset = Deployment.objects.all()
    serializer_class = DeploymentSerializer

class DeploymentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deployment.objects.all()
    serializer_class = DeploymentSerializer

