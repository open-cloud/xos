from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from plstackapi.planetstack.api.flavors import add_flavor, delete_flavor, get_flavors
from plstackapi.planetstack.serializers import FlavorSerializer
from plstackapi.util.request import parse_request


class FlavorListCreate(APIView):
    """ 
    List all flavors or create a new flavor.
    """

    def post(self, request, format = None):
        data = parse_request(request.DATA)  
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        elif 'flavor' in data:
            """Not Implemented"""
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            flavors = get_flavors(data['auth'])
            serializer = FlavorSerializer(flavors, many=True)
            return Response(serializer.data)
        
            
class FlavorRetrieveUpdateDestroy(APIView):
    """
    Retrieve, update or delete an flavor  
    """

    def post(self, request, pk, format=None):
        """Retrieve an flavor """
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        flavors = get_flavors(data['auth'], {'id': pk})
        if not flavors:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = FlavorSerializer(flavors[0])
        return Response(serializer.data)                  

    def put(self, request, pk, format=None):
        """update flavor not implemnted""" 
        return Response(status=status.HTTP_404_NOT_FOUND) 

    def delete(self, request, pk, format=None):
        """delete flavor not implemnted""" 
        return Response(status=status.HTTP_404_NOT_FOUND) 

            
            
        
