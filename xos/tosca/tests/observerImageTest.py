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

        self.run_model_policy()

        # first observer pass should make any necessary networks or ports
        self.run_observer()

        # reset the exponential backoff
        image = self.assert_obj(Image, "testimg")

        cims = ControllerImages.objects.filter(image=image)
        assert(len(cims) == 1)

if __name__ == "__main__":
    ObserverImageTest()

