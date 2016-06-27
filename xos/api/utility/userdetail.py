import json
import os
import sys
import traceback
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField
from django.core.exceptions import PermissionDenied


def getUserViewDict(user):
    # compute blessed_deployments by looking for the tenant view, and seeing what
    # deployments are attached to it.
    site_users=[]
    user_site_roles=[]
    user_site_id=None
    user_site_login_base=None
    if not user.site:
        pass # this is probably an error
    else:
        user_site_id = user.site.id
        user_site_login_base = user.site.login_base
        for auser in user.site.users.all():
            site_users.append(auser)

        for priv in user.site.siteprivileges.filter(user=user):
            user_site_roles.append(priv.role.role)
    return {"id": 0,
            "current_user_site_id": user_site_id,
            "current_user_login_base": user_site_login_base,
            "current_user_site_users": [auser.id for auser in site_users],
            "current_user_site_user_names": [auser.email for auser in site_users],
            "current_user_can_create_slice": user.is_admin or ("pi" in user_site_roles) or ("admin" in user_site_roles),
            "current_user_id": user.id,
            }

class UserList(APIView):
    method_kind = "list"
    method_name = "me"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        return Response( getUserViewDict(request.user) )

class UserDetail(APIView):
    method_kind = "detail"
    method_name = "me"

    def get(self, request, format=None, pk=0):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        return Response( [getUserViewDict(request.user)] )







