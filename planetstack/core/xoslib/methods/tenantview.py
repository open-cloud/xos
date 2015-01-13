from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework.views import APIView
from core.models import *
from django.forms import widgets
from syndicate_storage.models import Volume

# This REST API endpoint contains a bunch of misc information that the
# tenant view needs to display

BLESSED_DEPLOYMENTS = ["ViCCI"] # ["US-MaxPlanck", "US-GeorgiaTech", "US-Princeton", "US-Washington", "US-Stanford"]

def getTenantViewDict(user):
    blessed_sites = []
    for site in Site.objects.all():
        good=False
        for deployment in site.deployments.all():
            if deployment.name in BLESSED_DEPLOYMENTS:
                good=True
        if good:
            blessed_sites.append(site)

    blessed_images=[]
    for image in Image.objects.all():
        good = False
        for deployment in image.deployments.all():
            if deployment.name in BLESSED_DEPLOYMENTS:
                 good=True
        if good:
            blessed_images.append(image)

    blessed_flavors=[]
    for flavor in Flavor.objects.all():
        good = False
        for deployment in flavor.deployments.all():
            if deployment.name in BLESSED_DEPLOYMENTS:
                 good=True
        if good:
            blessed_flavors.append(flavor)

    volumes=[]
    for volume in Volume.objects.all():
        if not volume.private:
            volumes.append(volume)

    site_users=[]
    for auser in user.site.users.all():
        site_users.append(auser)

    blessed_service_classes = [ServiceClass.objects.get(name="Best Effort")]

    return {"id": 0,
            "blessed_deployment_names": BLESSED_DEPLOYMENTS,
            "blessed_site_names": [site.name for site in blessed_sites],
            "blessed_sites": [site.id for site in blessed_sites],
            "blessed_image_names": [image.name for image in blessed_images],
            "blessed_images": [image.id for image in blessed_images],
            "blessed_flavor_names": [flavor.name for flavor in blessed_flavors],
            "blessed_flavors": [flavor.id for flavor in blessed_flavors],
            "blessed_service_class_names": [serviceclass.name for serviceclass in blessed_service_classes],
            "blessed_service_classes": [serviceclass.id for serviceclass in blessed_service_classes],
            "public_volume_names": [volume.name for volume in volumes],
            "public_volumes": [volume.id for volume in volumes],
            "current_user_site_id": user.site.id,
            "current_user_login_base": user.site.login_base,
            "current_user_site_users": [auser.id for auser in site_users],
            "current_user_site_user_names": [auser.email for auser in site_users],
            }

class TenantList(APIView):
    method_kind = "list"
    method_name = "tenantview"

    def get(self, request, format=None):
        return Response( getTenantViewDict(request.user) )

class TenantDetail(APIView):
    method_kind = "detail"
    method_name = "tenantview"

    def get(self, request, format=None, pk=0):
        return Response( [getTenantViewDict(request.user)] )

