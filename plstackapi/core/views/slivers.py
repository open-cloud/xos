from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from plstackapi.core.api.slivers import add_sliver, delete_sliver, get_slivers, update_sliver
from plstackapi.core.serializers import SliverSerializer
from plstackapi.util.request import parse_request


class SliverListCreate(APIView):
    """ 
    List all slivers or create a new sliver.
    """

    def post(self, request, format = None):
        data = parse_request(request.DATA)  
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        elif 'sliver' in data:
            sliver = add_sliver(data['auth'], data['sliver'])
            serializer = SliverSerializer(sliver)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            slivers = get_slivers(data['auth'])
            serializer = SliverSerializer(slivers, many=True)
            return Response(serializer.data)
        
            
class SliverRetrieveUpdateDestroy(APIView):
    """
    Retrieve, update or delete a sliver 
    """

    def post(self, request, pk, format=None):
        """Retrieve a sliver"""
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        slivers = get_slivers(data['auth'], pk)
        if not slivers:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SliverSerializer(slivers[0])
        return Response(serializer.data)                  

    def put(self, request, pk, format=None):
        """update a sliver""" 
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif 'sliver' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        sliver = update_sliver(pk, data['sliver'])
        serializer = SliverSerializer(sliver)
        return Response(serializer.data) 

    def delete(self, request, pk, format=None):
        data = parse_request(request.DATA) 
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        delete_sliver(data['auth'], pk)
        return Response(status=status.HTTP_204_NO_CONTENT) 
            
            
        
