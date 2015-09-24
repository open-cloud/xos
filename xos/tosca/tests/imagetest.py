from basetest import BaseToscaTest

from core.models import Image

class ImageTest(BaseToscaTest):
    tests = ["create_image_minimal",
             "create_image_maximal",
             "destroy_image",
                           ]

    def cleanup(self):
        self.try_to_delete(Image, name="testimg")

    def create_image_minimal(self):
        self.assert_noobj(Image, "testimg")
        self.execute(self.make_nodetemplate("testimg", "tosca.nodes.Image"))
        instance = self.assert_obj(Image, "testimg", disk_format="", container_format="", path=None)

    def create_image_maximal(self):
        self.assert_noobj(Image, "testimg")
        self.execute(self.make_nodetemplate("testimg", "tosca.nodes.Image",
                                            props={"disk_format": "a", "container_format": "b", "path": "c"}))
        instance = self.assert_obj(Image, "testimg", disk_format="a", container_format="b", path="c")

    def destroy_image(self):
        self.assert_noobj(Image, "testimg")
        self.execute(self.make_nodetemplate("testimg", "tosca.nodes.Image"))
        instance = self.assert_obj(Image, "testimg", disk_format="", container_format="", path=None)
        self.destroy(self.make_nodetemplate("testimg", "tosca.nodes.Image"))
        self.assert_noobj(Image, "testimg")

if __name__ == "__main__":
    ImageTest()


