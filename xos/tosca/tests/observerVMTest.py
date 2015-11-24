from observertest import BaseObserverToscaTest

from core.models import Instance, Site

# Note that as a side effect, these tests will also create a Site

class ObserverVMTest(BaseObserverToscaTest):
    tests = ["create_vm"]
    # hide_observer_output = False # uncomment to display lots of stuff to screen

    def cleanup(self):
        # We don't want to leak resources, so we make sure to let the observer
        # attempt to delete these objects.
        self.try_to_delete(Instance, purge=False, name="test_compute1")
        self.try_to_delete(Site, purge=False, name="testsite")
        self.run_observer()
        # The site objects don't seem to go away nicely, they linger about and
        # cause an IntegrityError due to a duplicate login_base
        self.try_to_delete(Site, purge=True, name="testsite")

    def get_base_templates(self):
        return self.make_nodetemplate("testsite", "tosca.nodes.Site") + \
               self.make_nodetemplate("testsite_slice1", "tosca.nodes.Slice", reqs=[("testsite", "tosca.relationships.MemberOfSite")])

    def create_vm(self):
        self.assert_noobj(Instance, "test_compute1")
        self.execute(self.get_base_templates() +
                     self.make_compute("testsite_slice1", "test_compute1", disk_size="1 GB", mem_size="513 MB"))
        instance = self.assert_obj(Instance, "test_compute1")
        assert(instance.flavor.name == "m1.small")

        # first pass makes the Networks
        self.run_model_policy(save_output="/tmp/instancetest:create_vm:model_policy_first")

        # second pass makes the NetworkControllers
        self.run_model_policy(save_output="/tmp/instancetest:create_vm:model_policy_second")

        # first observer pass should make any necessary networks or ports
        self.run_observer(save_output="/tmp/instancetest:create_vm:observer_first")

        # reset the exponential backoff
        instance = self.assert_obj(Instance, "test_compute1")
        instance.backend_register="{}"
        instance.save()

        # third pass reset lazy_blocked
        self.run_model_policy(save_output="/tmp/instancetest:create_vm:model_policy_third")

        # second observer pass should instantiate the controller networks
        #    (might instantiate the instance, too)
        self.run_observer(save_output="/tmp/instancetest:create_vm:observer_second")

        # reset the exponential backoff
        instance = self.assert_obj(Instance, "test_compute1")
        instance.backend_register="{}"
        instance.save()

        # third observer pass should instantiate the instance
        self.run_observer(save_output="/tmp/instancetest:create_vm:observer_third")

        instance = self.assert_obj(Instance, "test_compute1")

        assert(instance.instance_id is not None)
        assert(instance.instance_name is not None)

        # there should be a port on the private network and a port on nat-net
        assert(instance.ports.count() == 2)

if __name__ == "__main__":
    ObserverVMTest()

