from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from plstackapi.core.api.nodes import add_node, delete_node, get_nodes, update_node
from plstackapi.core.serializers import NodeSerializer
from plstackapi.util.request import parse_request


class NodeListCreate(APIView):
    """ 
    List all nodes or create a new node.
    """

    def post(self, request, format = None):
        data = parse_request(request.DATA)  
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        elif 'node' in data:
            """Not Implemented"""
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            nodes = get_nodes(data['auth'])
            serializer = NodeSerializer(nodes, many=True)
            return Response(serializer.data)
        
            
class NodeRetrieveUpdateDestroy(APIView):
    """
    Retrieve, update or delete an node  
    """

    def post(self, request, pk, format=None):
        """Retrieve an node """
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        nodes = get_nodes(data['auth'], pk)
        if not nodes:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = NodeSerializer(nodes[0])
        return Response(serializer.data)                  

    def put(self, request, pk, format=None):
        """update node not implemnted""" 
        return Response(status=status.HTTP_404_NOT_FOUND) 

    def delete(self, request, pk, format=None):
        """delete node not implemnted""" 
        return Response(status=status.HTTP_404_NOT_FOUND) 

            
            
        
