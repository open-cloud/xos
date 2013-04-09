from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from plstackapi.planetstack.api.keys import add_key, delete_key, get_keys, update_key
from plstackapi.planetstack.serializers import KeySerializer
from plstackapi.util.request import parse_request


class KeyListCreate(APIView):
    """ 
    List all users or create a new key.
    """

    def post(self, request, format = None):
        data = parse_request(request.DATA)  
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        elif 'key' in data:
            key = add_key(data['auth'], data['key'])
            serializer = KeySerializer(key)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            keys = get_keys(data['auth'])
            serializer = KeySerializer(keys, many=True)
            return Response(serializer.data)
        
            
class KeyRetrieveUpdateDestroy(APIView):
    """
    Retrieve, update or delete a key 
    """

    def post(self, request, pk, format=None):
        """Retrieve a key"""
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        keys = get_keys(data['auth'], {'id': pk})
        if not keys:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = KeySerializer(keys[0])
        return Response(serializer.data)                  

    def put(self, request, pk, format=None):
        """update a key""" 
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif 'key' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        key = update_key(pk, data['key'])
        serializer = KeySerializer(key)
        return Response(serializer.data) 

    def delete(self, request, pk, format=None):
        data = parse_request(request.DATA) 
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        delete_key(data['auth'], {'id': pk})
        return Response(status=status.HTTP_204_NO_CONTENT) 
            
            
        
