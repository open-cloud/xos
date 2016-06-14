import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
django.setup()

for obj in ControllerNetwork.deleted_objects.all():
    print "Purging deleted object", obj
    obj.delete(purge=True)

for obj in ControllerSite.deleted_objects.all():
    print "Purging deleted object", obj
    obj.delete(purge=True)

for obj in ControllerSlice.deleted_objects.all():
    print "Purging deleted object", obj
    obj.delete(purge=True)

for obj in NetworkSlice.deleted_objects.all():
    print "Purging deleted object", obj
    obj.delete(purge=True)

for obj in Port.deleted_objects.all():
    print "Purging deleted object", obj
    obj.delete(purge=True)

for obj in DeploymentPrivilege.deleted_objects.all():
    print "Purging deleted object", obj
    obj.delete(purge=True)

for obj in SiteDeployment.deleted_objects.all():
    print "Purging deleted object", obj
    obj.delete(purge=True)

seen=[]
for obj in ControllerNetwork.objects.all():
     seen.append(obj.id)
     conflicts = ControllerNetwork.objects.filter(network=obj.network, controller=obj.controller)
     for conflict in conflicts:
         if conflict.id not in seen:
             print "Purging", conflict, conflict.id, "due to duplicate of", obj.id
             conflict.delete(purge=True)

seen=[]
for obj in NetworkSlice.objects.all():
     seen.append(obj.id)
     conflicts = NetworkSlice.objects.filter(network=obj.network, slice=obj.slice)
     for conflict in conflicts:
         if conflict.id not in seen:
             print "Purging", conflict, conflict.id, "due to duplicate of", obj.id
             conflict.delete(purge=True)

seen=[]
for obj in Port.objects.all():
     seen.append(obj.id)
     conflicts = Port.objects.filter(network=obj.network, instance=obj.instanc)
     for conflict in conflicts:
         if conflict.id not in seen:
             print "Purging", conflict, conflict.id, "due to duplicate of", obj.id
             conflict.delete(purge=True)

seen=[]
for obj in DeploymentPrivilege.objects.all():
     seen.append(obj.id)
     conflicts = DeploymentPrivilege.objects.filter(user=obj.user, deployment=obj.deployment, role=obj.role)
     for conflict in conflicts:
         if conflict.id not in seen:
             print "Purging", conflict, conflict.id, "due to duplicate of", obj.id
             conflict.delete(purge=True)

seen=[]
for obj in SiteDeployment.objects.all():
     seen.append(obj.id)
     conflicts = SiteDeployment.objects.filter(site=obj.site, deployment=obj.deployment, controller=obj.controller)
     for conflict in conflicts:
         if conflict.id not in seen:
             print "Purging", conflict, conflict.id, "due to duplicate of", obj.id
             conflict.delete(purge=True)

seen=[]
for obj in ControllerSite.objects.all():
     seen.append(obj.id)
     conflicts = ControllerSite.objects.filter(site=obj.site, controller=obj.controller)
     for conflict in conflicts:
         if conflict.id not in seen:
             print "Purging", conflict, conflict.id, "due to duplicate of", obj.id
             conflict.delete(purge=True)

seen=[]
for obj in ControllerSlice.objects.all():
     seen.append(obj.id)
     conflicts = ControllerSlice.objects.filter(slice=obj.slice, controller=obj.controller)
     for conflict in conflicts:
         if conflict.id not in seen:
             print "Purging", conflict, conflict.id, "due to duplicate of", obj.id
             conflict.delete(purge=True)

