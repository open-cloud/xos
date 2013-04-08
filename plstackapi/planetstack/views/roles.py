from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from plstackapi.planetstack.api.roles import add_role, delete_role, get_roles
from plstackapi.planetstack.serializers import RoleSerializer


class RoleListCreate(APIView):
    """ 
    List all roles or create a new role.
    """

    def post(self, request, format = None):
        
        if 'auth' not in request.DATA:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        else if 'name' in request.DATA:
            role = add_role(request.DATA['auth'], request.DATA['name'])
            serializer = RoleSerializer(data=role)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            roles = get_roles(request.DATA['auth'])
            serializer = RoleSerializer(roles, many=True)
            return Response(Serializer.data)
        
            
        
            
            
        
