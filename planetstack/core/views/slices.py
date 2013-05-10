from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.api.slices import add_slice, delete_slice, get_slices, update_slice
from core.serializers import SliceSerializer
from util.request import parse_request


class SliceListCreate(APIView):
    """ 
    List all slices or create a new slice.
    """

    def post(self, request, format = None):
        data = parse_request(request.DATA)  
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        elif 'slice' in data:
            slice = add_slice(data['auth'], data['slice'])
            serializer = SliceSerializer(slice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            slices = get_slices(data['auth'])
            serializer = SliceSerializer(slices, many=True)
            return Response(serializer.data)
        
            
class SliceRetrieveUpdateDestroy(APIView):
    """
    Retrieve, update or delete a slice 
    """

    def post(self, request, pk, format=None):
        """Retrieve a slice"""
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        slices = get_slices(data['auth'],  pk)
        if not slices:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SliceSerializer(slices[0])
        return Response(serializer.data)                  

    def put(self, request, pk, format=None):
        """update a slice""" 
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif 'slice' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        slice = update_slice(pk, data['slice'])
        serializer = SliceSerializer(slice)
        return Response(serializer.data) 

    def delete(self, request, pk, format=None):
        data = parse_request(request.DATA) 
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        delete_slice(data['auth'],  pk)
        return Response(status=status.HTTP_204_NO_CONTENT) 
            
            
        
