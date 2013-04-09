from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from plstackapi.planetstack.api.roles import add_site, delete_site, get_sites
from plstackapi.planetstack.serializers import SiteSerializer
from plstackapi.util.request import parse_request


class SiteListCreate(APIView):
    """ 
    List all roles or create a new site.
    """

    def post(self, request, format = None):
        data = parse_request(request.DATA)  
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        elif 'site' in data:
            site = add_site(data['auth'], data['site'])
            serializer = SiteSerializer(data=site)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            sites = get_sites(data['auth'])
            serializer = SiteSerializer(sites, many=True)
            return Response(serializer.data)
        
            
class SiteRetrieveUpdateDestroy(APIView):
    """
    Retrieve, update or delete a site 
    """

    def post(self, request, pk, format=None):
        """Retrieve a site"""
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        sites = get_sites(data['auth'], {'tenant_id': pk})
        if not sites:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SiteSerializer(sites[0])
        return Response(serializer.data)                  

    def put(self, request, pk, format=None):
        """update a role""" 
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif 'site' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        site = update_site(pk, data['site'])
        serializer = SiteSerializer(data=site)
        return Response(serializer.data) 

    def delete(self, request, pk, format=None):
        data = parse_request(request.DATA) 
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        delete_site(data['auth'], {'tenant_id': pk})
        return Response(status=status.HTTP_204_NO_CONTENT) 
            
            
        
