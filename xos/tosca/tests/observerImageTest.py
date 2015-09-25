from observertest import BaseObserverToscaTest

from core.models import Image, Deployment, ControllerImages

# Note that as a side effect, these tests will also create a Site

class ObserverImageTest(BaseObserverToscaTest):
    tests = ["create_image"]
    # hide_observer_output = False # uncomment to display lots of stuff to screen

    def cleanup(self):
        # We don't want to leak resources, so we make sure to let the observer
        # attempt to delete these objects.
        self.try_to_delete(Image, purge=False, name="testimg")
        self.run_observer()
        self.try_to_delete(Image, purge=True, name="testimg")

    def create_image(self):
        self.assert_noobj(Image, "testimg")
        file("/tmp/testimg","w").write("this_is_a_test")
        self.execute(self.make_nodetemplate(self.get_usable_deployment(), "tosca.nodes.Deployment",
                                            props={"no-delete": True},
                                            reqs=[("testimg", "tosca.relationships.SupportsImage")]) +
                     self.make_nodetemplate("testimg", "tosca.nodes.Image",
                                            props={"path": "/tmp/testimg"}))
        image = self.assert_obj(Image, "testimg")

        self.run_model_policy(save_output="/tmp/imagetest:create_image:model_policy")

        # make sure a ControllerImages object was created
        cims = ControllerImages.objects.filter(image=image)
        assert(len(cims) == 1)

        # first observer pass should make any necessary networks or ports
        self.run_observer(save_output="/tmp/imagetest:create_image:observer")

        # reset the exponential backoff
        image = self.assert_obj(Image, "testimg")

        # make sure the ControllerImages object has its image_id filled in
        cims = ControllerImages.objects.filter(image=image)
        assert(len(cims) == 1)
        assert(cims[0].glance_image_id is not None)
        assert(cims[0].glance_image_id != "")

if __name__ == "__main__":
    ObserverImageTest()

