from observertest import BaseObserverToscaTest

from core.models import Instance, Site

# Note that as a side effect, these tests will also create a Site

class ObserverContainerTest(BaseObserverToscaTest):
    tests = ["create_container"]
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
               self.make_nodetemplate("testsite_slice1", "tosca.nodes.Slice", reqs=[("testsite", "tosca.relationships.MemberOfSite")]) + \
               self.make_nodetemplate("andybavier/docker-vcpe", "tosca.nodes.Image", props={"kind": "container", "container_format": "na", "disk_format": "na"})

    def create_container(self):
        self.assert_noobj(Instance, "test_compute1")
        self.execute(self.get_base_templates() +
                     self.make_compute("testsite_slice1", "test_compute1", disk_size="1 GB", mem_size="513 MB", isolation="container",
                                       reqs=[("andybavier/docker-vcpe", "tosca.relationships.UsesImage")],
                                       ))
        instance = self.assert_obj(Instance, "test_compute1")
        assert(instance.flavor.name == "m1.small")

        # first pass makes the Networks
        self.run_model_policy(save_output="/tmp/instancetest:create_container:model_policy_first")

        # XXX deal with bug where
        instance = self.assert_obj(Instance, "test_compute1")
        instance.save()

        # second pass makes the NetworkControllers
        self.run_model_policy(save_output="/tmp/instancetest:create_container:model_policy_second")

        # first observer pass should make any necessary networks or ports
        self.run_observer(save_output="/tmp/instancetest:create_container:observer_first")

        # reset the exponential backoff
        instance = self.assert_obj(Instance, "test_compute1")
        instance.backend_register="{}"
        instance.save()

        # we need to reset the companion instance's exponential backoff too
        companion_instance = Instance.objects.filter(slice=instance.slice, isolation="vm")
        assert(companion_instance)
        companion_instance = companion_instance[0]
        companion_instance.backend_register="{}"
        companion_instance.save()

        # third pass reset lazy_blocked
        self.run_model_policy(save_output="/tmp/instancetest:create_container:model_policy_third")

        # second observer pass should instantiate the controller networks
        #    (might instantiate the instance, too)
        self.run_observer(save_output="/tmp/instancetest:create_container:observer_second")

        # reset the exponential backoff
        instance = self.assert_obj(Instance, "test_compute1")
        instance.backend_register="{}"
        instance.save()

        # we need to reset the companion instance's exponential backoff too
        companion_instance = Instance.objects.filter(slice=instance.slice, isolation="vm")
        assert(companion_instance)
        companion_instance = companion_instance[0]
        companion_instance.backend_register="{}"
        companion_instance.save()

        # third observer pass should instantiate the companion instance
        self.run_observer(save_output="/tmp/instancetest:create_container:observer_third")

        # third observer pass should instantiate the instance
        self.run_observer(save_output="/tmp/instancetest:create_container:observer_fourth")

        instance = self.assert_obj(Instance, "test_compute1")

        assert(instance.instance_id is not None)
        assert(instance.instance_name is not None)

        # there should be one port on the private network
        assert(instance.ports.count() == 1)

if __name__ == "__main__":
    ObserverContainerTest()

