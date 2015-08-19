from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'deployments': reverse('deployment-list', request=request, format=format),
        'images': reverse('image-list', request=request, format=format),
        'nodes': reverse('node-list', request=request, format=format),
        'projects': reverse('project-list', request=request, format=format),
        'reservations': reverse('reservation-list', request=request, format=format),
        'roles': reverse('role-list', request=request, format=format),
        'serviceclasses': reverse('serviceclass-list', request=request, format=format),
        'serviceresources': reverse('serviceresource-list', request=request, format=format),
        'sites': reverse('site-list', request=request, format=format),
        'slices': reverse('slice-list', request=request, format=format),
        'instances': reverse('instance-list', request=request, format=format),
        'tags': reverse('tag-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
    })
