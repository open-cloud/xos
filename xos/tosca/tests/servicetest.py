from basetest import BaseToscaTest

from core.models import Service

class ServiceTest(BaseToscaTest):
    tests = ["create_service_minimal",
             "create_service_notpublished"]

    def cleanup(self):
        self.try_to_delete(Service, name="test_svc")

    def create_service_minimal(self):
        self.assert_noobj(Service, "test_svc")
        self.execute(self.make_nodetemplate("test_svc", "tosca.nodes.Service"))
        self.assert_obj(Service, "test_svc", kind="generic", published=True, enabled=True)

    def create_service_notpublished(self):
        self.assert_noobj(Service, "test_svc")
        self.execute(self.make_nodetemplate("test_svc", "tosca.nodes.Service", {"published": False}))
        self.assert_obj(Service, "test_svc", kind="generic", published=False, enabled=True)

if __name__ == "__main__":
    ServiceTest()


