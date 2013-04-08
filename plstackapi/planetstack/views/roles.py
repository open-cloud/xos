from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from plstackapi.planetstack.models import Role


class RoleListCreate(APIView):
    """ 
    List all roles or create a new role.
    """

    def post(self, request, format = None):
        print request
        
