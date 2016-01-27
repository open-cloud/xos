from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.core import serializers
from rest_framework import generics
from rest_framework.views import APIView
from core.models import *
from services.hpc.models import *
from services.requestrouter.models import *
from django.forms import widgets
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
import json
import socket
import time
import django.middleware.csrf
from xos.exceptions import *
from django.forms.models import model_to_dict

def serialize_user(model):
    serialized = model_to_dict(model)
    del serialized['last_login']
    del serialized['timezone']
    del serialized['password']
    print serialized
    return json.dumps(serialized)

class LoginView(APIView):
    method_kind = "list"
    method_name = "login"

    def do_login(self, request, username, password):
        if not username:
            raise XOSMissingField("No username specified")

        if not password:
            raise XOSMissingField("No password specified")

        u = User.objects.filter(email=username)
        if not u:
            raise PermissionDenied("Permission Denied")

        u=u[0]

        if not u.check_password(password):
            raise PermissionDenied("Permission Denied")

        auth = {"username": username, "password": password}
        request.session["auth"] = auth
        request.session.save()

        return Response({
            "xoscsrftoken": django.middleware.csrf.get_token(request),
            "xossessionid": request.session.session_key,
            "user": serialize_user(u)
        })

    def get(self, request, format=None):
        username = request.GET.get("username", None)
        password = request.GET.get("password", None)

        return self.do_login(request, username, password)

    def post(self, request, format=None):
        username = request.DATA.get("username", None)
        password = request.DATA.get("password", None)

        return self.do_login(request, username, password)


