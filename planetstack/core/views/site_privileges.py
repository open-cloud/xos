from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.api.site_privileges import add_site_privilege, delete_site_privilege, get_site_privileges, update_site_privilege
from core.serializers import SitePrivilegeSerializer
from util.request import parse_request


class SitePrivilegeListCreate(APIView):
    """ 
    List all site_privileges or create a new site_privilege.
    """

    def post(self, request, format = None):
        data = parse_request(request.DATA)  
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        elif 'site_privilege' in data:
            site_privilege = add_site_privilege(data['auth'], data['site_privilege'])
            serializer = SitePrivilegeSerializer(site_privilege)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            site_privileges = get_site_privileges(data['auth'])
            serializer = SitePrivilegeSerializer(site_privileges, many=True)
            return Response(serializer.data)
        
            
class SitePrivilegeRetrieveUpdateDestroy(APIView):
    """
    Retrieve, update or delete a site_privilege 
    """

    def post(self, request, pk, format=None):
        """Retrieve a site_privilege"""
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        site_privileges = get_site_privileges(data['auth'], pk)
        if not site_privileges:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SitePrivilegeSerializer(site_privileges[0])
        return Response(serializer.data)                  

    def put(self, request, pk, format=None):
        """update a site_privilege""" 
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif 'site_privilege' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        site_privilege = update_site_privilege(pk, data['site_privilege'])
        serializer = SitePrivilegeSerializer(site_privilege)
        return Response(serializer.data) 

    def delete(self, request, pk, format=None):
        data = parse_request(request.DATA) 
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        delete_site_privilege(data['auth'], pk)
        return Response(status=status.HTTP_204_NO_CONTENT) 
            
            
        
