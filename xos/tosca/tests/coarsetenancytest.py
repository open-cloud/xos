
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


from basetest import BaseToscaTest

from core.models import Service, CoarseTenant

class CoarseTenancyTest(BaseToscaTest):
    tests = ["create_coarsetenant",
             "update_coarsetenant"]

    def cleanup(self):
        self.try_to_delete(Service, name="test_svc1")
        self.try_to_delete(Service, name="test_svc2")

    def create_coarsetenant(self):
        self.assert_noobj(Service, "test_svc1")
        self.assert_noobj(Service, "test_svc2")
        self.execute(self.make_nodetemplate("test_svc1", "tosca.nodes.Service", reqs=[("test_svc2", "tosca.relationships.TenantOfService")]) +
                     self.make_nodetemplate("test_svc2", "tosca.nodes.Service"))
        svc1 = self.assert_obj(Service, "test_svc1", kind="generic", published=True, enabled=True)
        svc2 = self.assert_obj(Service, "test_svc2", kind="generic", published=True, enabled=True)

        ct = CoarseTenant.objects.filter(provider_service=svc2, subscriber_service=svc1)
        assert(ct)

    def update_coarsetenant(self):
        # first make the services without the coarse tenancy relationship
        self.assert_noobj(Service, "test_svc1")
        self.assert_noobj(Service, "test_svc2")
        self.execute(self.make_nodetemplate("test_svc1", "tosca.nodes.Service") +
                     self.make_nodetemplate("test_svc2", "tosca.nodes.Service"))
        svc1 = self.assert_obj(Service, "test_svc1", kind="generic", published=True, enabled=True)
        svc2 = self.assert_obj(Service, "test_svc2", kind="generic", published=True, enabled=True)
        ct = CoarseTenant.objects.filter(provider_service=svc2, subscriber_service=svc1)
        assert(not ct)

        # now add the relationship
        self.execute(self.make_nodetemplate("test_svc1", "tosca.nodes.Service", reqs=[("test_svc2", "tosca.relationships.TenantOfService")])+
                                            self.make_nodetemplate("test_svc2", "tosca.nodes.Service"))
        updated_svc1 = self.assert_obj(Service, "test_svc1", kind="generic", published=True, enabled=True)

        assert(svc1.id == updated_svc1.id)

        ct = CoarseTenant.objects.filter(provider_service=svc2, subscriber_service=svc1)
        assert(ct)


if __name__ == "__main__":
    CoarseTenancyTest()


