from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
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
            raise XOSNotFound("User %s does not exist" % username)

        u=u[0]

        if not u.check_password(password):
            raise PermissionDenied("Incorrect password")

        auth = {"username": username, "password": password}
        request.session["auth"] = auth
        request.session.save()

        return Response({"xoscsrftoken": django.middleware.csrf.get_token(request),
                         "xossessionid": request.session.session_key})

    def get(self, request, format=None):
        username = request.GET.get("username", None)
        password = request.GET.get("password", None)

        return self.do_login(request, username, password)

    def post(self, request, format=None):
        username = request.DATA.get("username", None)
        password = request.DATA.get("password", None)

        return self.do_login(request, username, password)


