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


