from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'roles': reverse('role-list', request=request, format=format),
        #'nodes': reverse('node-list', request=request, format=format),
        'sites': reverse('site-list', request=request, format=format),
        'deploymentNetworks': reverse('deploymentnetwork-list', request=request, format=format),
        #'slices': reverse('slice-list', request=request, format=format)
        'images': reverse('image-list', request=request, format=format),
    })
