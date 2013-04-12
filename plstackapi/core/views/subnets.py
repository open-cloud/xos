from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from plstackapi.core.api.subnets import add_subnet, delete_subnet, get_subnets, update_subnet
from plstackapi.core.serializers import SubnetSerializer
from plstackapi.util.request import parse_request


class SubnetListCreate(APIView):
    """ 
    List all subnets or create a new subnet.
    """

    def post(self, request, format = None):
        data = parse_request(request.DATA)  
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        elif 'subnet' in data:
            subnet = add_subnet(data['auth'], data['subnet'])
            serializer = SubnetSerializer(subnet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            subnets = get_subnets(data['auth'])
            serializer = SubnetSerializer(subnets, many=True)
            return Response(serializer.data)
        
            
class SubnetRetrieveUpdateDestroy(APIView):
    """
    Retrieve, update or delete a subnet 
    """

    def post(self, request, pk, format=None):
        """Retrieve a subnet"""
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subnets = get_subnets(data['auth'], {'id': pk})
        if not subnets:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SubnetSerializer(subnets[0])
        return Response(serializer.data)                  

    def put(self, request, pk, format=None):
        """update a subnet""" 
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif 'subnet' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        subnet = update_subnet(pk, data['subnet'])
        serializer = SubnetSerializer(subnet)
        return Response(serializer.data) 

    def delete(self, request, pk, format=None):
        data = parse_request(request.DATA) 
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        delete_subnet(data['auth'], {'id': pk})
        return Response(status=status.HTTP_204_NO_CONTENT) 
            
            
        
