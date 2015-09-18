from observertest import BaseObserverToscaTest

from core.models import Instance, Site

class ObserverComputeTest(BaseObserverToscaTest):
    tests = ["create_instance"]
    # hide_observer_output = False # uncomment to display lots of stuff to screen

    def cleanup(self):
        self.try_to_delete(Instance, purge=False, name="test_compute1")
        self.try_to_delete(Site, purge=False, name="testsite")
        self.run_observer()
        self.try_to_delete(Site, purge=True, name="testsite")   # make it go away

    def get_base_templates(self):
        return self.make_nodetemplate("testsite", "tosca.nodes.Site") + \
               self.make_nodetemplate("testsite_slice1", "tosca.nodes.Slice", reqs=[("testsite", "tosca.relationships.MemberOfSite")])

    def create_instance(self):
        self.assert_noobj(Instance, "test_compute1")
        self.execute(self.get_base_templates() +
                     self.make_compute("testsite_slice1", "test_compute1", disk_size="1 GB", mem_size="513 MB"))
        instance = self.assert_obj(Instance, "test_compute1")
        assert(instance.flavor.name == "m1.small")

        self.run_model_policy()

        # this should make the ports
        self.run_observer()

        # reset the exponential backoff
        instance = self.assert_obj(Instance, "test_compute1")
        instance.backend_register="{}"

        # this should instantiate the instance
        self.run_observer()

        instance = self.assert_obj(Instance, "test_compute1")

        assert(instance.instance_id is not None)
        assert(instance.instance_name is not None)

if __name__ == "__main__":
    ObserverComputeTest()

