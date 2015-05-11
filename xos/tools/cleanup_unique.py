import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
from hpc.models import *
from cord.models import *
django.setup()


for obj in ControllerNetwork.objects.all():
     conflicts = ControllerNetwork.objects.filter(network=obj.network, controller=obj.controller)
     for conflict in conflicts:
         if conflict.id != obj.id:
             print "Purging", conflict
             conflict.delete(purge=True)

for obj in NetworkSlice.objects.all():
     conflicts = NetworkSlice.objects.filter(network=obj.network, slice=obj.slice)
     for conflict in conflicts:
         if conflict.id != obj.id:
             print "Purging", conflict        
             conflict.delete(purge=True)

for obj in NetworkSliver.objects.all():
     conflicts = NetworkSliver.objects.filter(network=obj.network, sliver=obj.sliver)
     for conflict in conflicts:
         if conflict.id != obj.id:
             print "Purging", conflict 
             conflict.delete(purge=True)

for obj in DeploymentPrivilege.objects.all():
     conflicts = DeploymentPrivilege.objects.filter(user=obj.user, deployment=obj.deployment, role=obj.role)
     for conflict in conflicts:
         if conflict.id != obj.id:
             print "Purging", conflict 
             conflict.delete(purge=True)

for obj in SiteDeployment.objects.all():
     conflicts = SiteDeployment.objects.filter(site=obj.site, deployment=obj.deployment, controller=obj.controller)
     for conflict in conflicts:
         if conflict.id != obj.id:
             print "Purging", conflict 
             conflict.delete(purge=True)
