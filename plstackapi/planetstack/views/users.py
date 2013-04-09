from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from plstackapi.planetstack.api.user import add_user, delete_user, get_users, update_user
from plstackapi.planetstack.serializers import UserSerializer
from plstackapi.util.request import parse_request


class UserListCreate(APIView):
    """ 
    List all users or create a new user.
    """

    def post(self, request, format = None):
        data = parse_request(request.DATA)  
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        elif 'user' in data:
            user = add_user(data['auth'], data['user'])
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            users = get_users(data['auth'])
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        
            
class UserRetrieveUpdateDestroy(APIView):
    """
    Retrieve, update or delete a user 
    """

    def post(self, request, pk, format=None):
        """Retrieve a user"""
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        users = get_users(data['auth'], {'id': pk})
        if not users:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(users[0])
        return Response(serializer.data)                  

    def put(self, request, pk, format=None):
        """update a user""" 
        data = parse_request(request.DATA)
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif 'user' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = update_user(pk, data['user'])
        serializer = UserSerializer(user)
        return Response(serializer.data) 

    def delete(self, request, pk, format=None):
        data = parse_request(request.DATA) 
        if 'auth' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        delete_user(data['auth'], {'id': pk})
        return Response(status=status.HTTP_204_NO_CONTENT) 
            
            
        
