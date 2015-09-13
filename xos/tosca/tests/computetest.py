from basetest import BaseToscaTest

from core.models import Instance, Slice

class ComputeTest(BaseToscaTest):
    tests = [ # "create_compute_m1_tiny", XXX m1.tiny does not exist on cloudlab
             "create_compute_m1_small",
             "create_compute_m1_large_8192MB",
             "create_compute_m1_large_8GB",
             "destroy_compute",
             "create_compute_scalable",
             "destroy_compute_scalable",
                           ]

    def cleanup(self):
        self.try_to_delete(Instance, name="test_compute1")
        self.try_to_delete(Instance, name="test_compute1-0")
        self.try_to_delete(Instance, name="test_compute1-1")
        self.try_to_delete(Instance, name="test_compute1-2")
        self.try_to_delete(Instance, name="test_compute1-3")
        self.try_to_delete(Slice, name="testsite_slice1")

    def get_base_templates(self):
        return self.make_nodetemplate("testsite", "tosca.nodes.Site") + \
               self.make_nodetemplate("testsite_slice1", "tosca.nodes.Slice", reqs=[("testsite", "tosca.relationships.MemberOfSite")])

    def create_compute_m1_tiny(self):
        self.assert_noobj(Instance, "test_compute1")
        self.execute(self.get_base_templates() +
                     self.make_compute("testsite_slice1", "test_compute1", disk_size="1 GB", mem_size="500 MB"))
        instance = self.assert_obj(Instance, "test_compute1")
        assert(instance.flavor.name == "m1.tiny")

    def create_compute_m1_small(self):
        self.assert_noobj(Instance, "test_compute1")
        self.execute(self.get_base_templates() +
                     self.make_compute("testsite_slice1", "test_compute1", disk_size="1 GB", mem_size="513 MB"))
        instance = self.assert_obj(Instance, "test_compute1")
        assert(instance.flavor.name == "m1.small")

    def create_compute_m1_large_8192MB(self):
        self.assert_noobj(Instance, "test_compute1")
        self.execute(self.get_base_templates() +
                     self.make_compute("testsite_slice1", "test_compute1", mem_size="8192 MB"))
        instance = self.assert_obj(Instance, "test_compute1")
        assert(instance.flavor.name == "m1.large")

    def create_compute_m1_large_8GB(self):
        self.assert_noobj(Instance, "test_compute1")
        self.execute(self.get_base_templates() +
                     self.make_compute("testsite_slice1", "test_compute1", mem_size="8 GB"))
        instance = self.assert_obj(Instance, "test_compute1")
        assert(instance.flavor.name == "m1.large")

    def destroy_compute(self):
        self.execute(self.get_base_templates() +
                     self.make_compute("testsite_slice1", "test_compute1"))
        self.assert_obj(Instance, "test_compute1")
        self.destroy(self.get_base_templates() +
                     self.make_compute("testsite_slice1", "test_compute1"))
        self.assert_noobj(Instance, "test_compute1")

    def create_compute_scalable(self):
        self.assert_noobj(Instance, "test_compute1-1")
        self.assert_noobj(Instance, "test_compute1-2")
        self.assert_noobj(Instance, "test_compute1-3")
        self.execute(self.get_base_templates() +
                     self.make_compute("testsite_slice1", "test_compute1", mem_size="8 GB",
                                       caps={"scalable": {"min_instances": 2, "max_instances": 3, "default_instances": 2}}))
        # there should be two instances
        instance0 = self.assert_obj(Instance, "test_compute1-0")
        instance1 = self.assert_obj(Instance, "test_compute1-1")
        self.assert_noobj(Instance, "test_compute1-2")

    def destroy_compute_scalable(self):
        self.assert_noobj(Instance, "test_compute1-1")
        self.assert_noobj(Instance, "test_compute1-2")
        self.assert_noobj(Instance, "test_compute1-3")
        self.execute(self.get_base_templates() +
                     self.make_compute("testsite_slice1", "test_compute1", mem_size="8 GB",
                                       caps={"scalable": {"min_instances": 2, "max_instances": 3, "default_instances": 2}}))
        # there should be two instances
        instance0 = self.assert_obj(Instance, "test_compute1-0")
        instance1 = self.assert_obj(Instance, "test_compute1-1")

        self.destroy(self.get_base_templates() +
                     self.make_compute("testsite_slice1", "test_compute1", mem_size="8 GB",
                                       caps={"scalable": {"min_instances": 2, "max_instances": 3, "default_instances": 2}}))

        self.assert_noobj(Instance, "test_compute1-0")
        self.assert_noobj(Instance, "test_compute1-1")

if __name__ == "__main__":
    ComputeTest()


