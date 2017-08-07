
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
for obj in Privilege.objects.all():
     seen.append(obj.id)
     conflicts = Privilege.objects.filter(accessor_id=obj.accessor_id, object_id=obj.object_id, permission=obj.permission, accessor_type=obj.accessor_type, object_type=obj.object_type)
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

