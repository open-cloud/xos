
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

from xos.exceptions import *
from deployment_decl import *
from core.acl import AccessControlList

class Deployment(Deployment_decl):
    class Meta:
        proxy = True

    def get_acl(self):
        return AccessControlList(self.accessControl)

    def test_acl(self, slice=None, user=None):
        potential_users=[]

        if user:
            potential_users.append(user)

        if slice:
            potential_users.append(slice.creator)
            for priv in slice.sliceprivileges.all():
                if priv.user not in potential_users:
                    potential_users.append(priv.user)

        acl = self.get_acl()
        for user in potential_users:
            if acl.test(user) == "allow":
                return True

        return False

    @staticmethod
    def select_by_acl(user):
        ids = []
        for deployment in Deployment.objects.all():
            acl = deployment.get_acl()
            if acl.test(user) == "allow":
                ids.append(deployment.id)

        return Deployment.objects.filter(id__in=ids)
