from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from plstackapi.core.api.roles import add_role, delete_role, get_roles
from plstackapi.core.serializers import RoleSerializer
from plstackapi.util.request import parse_request


class RoleListCreate(APIView):
    """ 
    List all roles or create a new role.
    """

    def post(self, request, format = None):
        data = parse_request(request.DATA)  
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        elif 'role' in data:
            role = add_role(data['auth'], data['role']['role_type'])
            serializer = RoleSerializer(data=role)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            roles = get_roles(data['auth'])
            serializer = RoleSerializer(roles, many=True)
            return Response(serializer.data)
        
            
class RoleRetrieveUpdateDestroy(APIView):
    """
    Retrieve, update or delete a role 
    """

    def post(self, request, pk, format=None):
        """Retrieve a role"""
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        roles = get_roles(data['auth'], pk)
        if not roles:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializer(roles[0])
        return Response(serializer.data)                  

    def put(self, request, pk, format=None):
        """role update not implemnted""" 
        return Response(status=status.HTTP_404_NOT_FOUND) 

    def delete(self, request, pk, format=None):
        data = parse_request(request.DATA) 
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        delete_role(data['auth'], pk)
        return Response(status=status.HTTP_204_NO_CONTENT) 
            
            
        
