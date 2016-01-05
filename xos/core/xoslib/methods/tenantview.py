from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework.views import APIView
from core.models import *
from django.forms import widgets
from services.syndicate_storage.models import Volume
from django.core.exceptions import PermissionDenied

# This REST API endpoint contains a bunch of misc information that the
# tenant view needs to display

def getTenantViewDict(user):
    # compute blessed_deployments by looking for the tenant view, and seeing what
    # deployments are attached to it.
    blessed_deployments=[]
    for dash in DashboardView.objects.all():
        if (dash.url=="template:xosTenant"):
            for deployment in dash.deployments.all():
                if deployment not in blessed_deployments:
                    blessed_deployments.append(deployment)

    blessed_deployment_ids = [d.id for d in blessed_deployments]

    blessed_sites = []
    for site in Site.objects.all():
        good=False
        for deployment in site.deployments.all():
            if deployment.id in blessed_deployment_ids:
                # only bless sites that have at least one node in the deployment
                sitedeployments = SiteDeployment.objects.filter(site=site, deployment=deployment)
                for sd in sitedeployments.all():
                    if sd.nodes.count()>0:
                        good=True
        if good:
            blessed_sites.append(site)

    blessed_images=[]
    for image in Image.objects.all():
        good = False
        for deployment in image.deployments.all():
            if deployment.id in blessed_deployment_ids:
                 good=True
        if good:
            blessed_images.append(image)

    blessed_flavors=[]
    for flavor in Flavor.objects.all():
        good = False
        for deployment in flavor.deployments.all():
            if deployment.id in blessed_deployment_ids:
                 good=True
        if good:
            blessed_flavors.append(flavor)

    volumes=[]
    for volume in Volume.objects.all():
        if not volume.private:
            volumes.append(volume)

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

    blessed_service_classes = [ServiceClass.objects.get(name="Best Effort")]

    return {"id": 0,
            "blessed_deployment_names": [deployment.name for deployment in blessed_deployments],
            "blessed_deployments": [deployment.id for deployment in blessed_deployments],
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
            "current_user_site_id": user_site_id,
            "current_user_login_base": user_site_login_base,
            "current_user_site_users": [auser.id for auser in site_users],
            "current_user_site_user_names": [auser.email for auser in site_users],
            "current_user_can_create_slice": user.is_admin or ("pi" in user_site_roles) or ("admin" in user_site_roles),
            "current_user_id": user.id,
            }

class TenantList(APIView):
    method_kind = "list"
    method_name = "tenantview"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        return Response( getTenantViewDict(request.user) )

class TenantDetail(APIView):
    method_kind = "detail"
    method_name = "tenantview"

    def get(self, request, format=None, pk=0):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        return Response( [getTenantViewDict(request.user)] )

