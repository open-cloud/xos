from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from plstackapi.core.api.slice_memberships import add_slice_membership, delete_slice_membership, get_slice_memberships, update_slice_membership
from plstackapi.core.serializers import SliceMembershipSerializer
from plstackapi.util.request import parse_request


class SliceMembershipListCreate(APIView):
    """ 
    List all slice_memberships or create a new slice_membership.
    """

    def post(self, request, format = None):
        data = parse_request(request.DATA)  
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        elif 'slice_membership' in data:
            slice_membership = add_slice_membership(data['auth'], data['slice_membership'])
            serializer = SliceMembershipSerializer(slice_membership)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            slice_memberships = get_slice_memberships(data['auth'])
            serializer = SliceMembershipSerializer(slice_memberships, many=True)
            return Response(serializer.data)
        
            
class SliceMembershipRetrieveUpdateDestroy(APIView):
    """
    Retrieve, update or delete a slice_membership 
    """

    def post(self, request, pk, format=None):
        """Retrieve a slice_membership"""
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        slice_memberships = get_slice_memberships(data['auth'], pk)
        if not slice_memberships:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SliceMembershipSerializer(slice_memberships[0])
        return Response(serializer.data)                  

    def put(self, request, pk, format=None):
        """update a slice_membership""" 
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif 'slice_membership' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        slice_membership = update_slice_membership(pk, data['slice_membership'])
        serializer = SliceMembershipSerializer(slice_membership)
        return Response(serializer.data) 

    def delete(self, request, pk, format=None):
        data = parse_request(request.DATA) 
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        delete_slice_membership(data['auth'], pk)
        return Response(status=status.HTTP_204_NO_CONTENT) 
            
            
        
