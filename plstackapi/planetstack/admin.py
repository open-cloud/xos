from plstackapi.planetstack.models import *
from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

admin.site.register(Role)
admin.site.register(Site)
admin.site.register(Slice)
admin.site.register(Node)
admin.site.register(DeploymentNetwork)
admin.site.register(SiteDeploymentNetwork)
admin.site.register(Sliver)

