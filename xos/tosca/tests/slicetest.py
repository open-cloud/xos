from basetest import BaseToscaTest

from core.models import Slice, Site, User, SlicePrivilege

class SliceTest(BaseToscaTest):
    tests = ["create_slice_minimal",
             "create_slice_maximal",
             "create_slice_privilege",
             "create_slice_nocreate",
             "update_slice",
             "update_slice_noupdate",
             "destroy_slice",
             "destroy_slice_nodelete"]

    def cleanup(self):
        self.try_to_delete(Slice, name="testsite_testslice")
        self.try_to_delete(Site, name="testsite")

    def get_base_templates(self):
        return self.make_nodetemplate("testsite", "tosca.nodes.Site")

    def create_slice_minimal(self):
        self.assert_noobj(Slice, "testsite_testslice")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testsite_testslice", "tosca.nodes.Slice",
                                            reqs=[("testsite", "tosca.relationships.MemberOfSite")]))
        self.assert_obj(Slice, "testsite_testslice", enabled=True, description="", slice_url="", max_instances=10)

    def create_slice_maximal(self):
        self.assert_noobj(Slice, "testsite_testslice")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testsite_testslice", "tosca.nodes.Slice",
                                             props={"enabled": False, "description": "foo", "slice_url": "http://foo.com/", "max_instances": 11},
                                             reqs=[("testsite", "tosca.relationships.MemberOfSite")]))
        self.assert_obj(Slice, "testsite_testslice", enabled=False, description="foo", slice_url="http://foo.com/", max_instances=11)

    def create_slice_privilege(self):
        self.assert_noobj(Slice, "testsite_testslice")
        self.execute(self.get_base_templates() +
                     self.make_user_template() +
                     self.make_nodetemplate("testsite_testslice", "tosca.nodes.Slice",
                                            reqs=[("testsite", "tosca.relationships.MemberOfSite"),
                                                  ("test@user.com", "tosca.relationships.AdminPrivilege")]))
        slice = self.assert_obj(Slice, "testsite_testslice")
        user = User.objects.get(email="test@user.com")

        dps = SlicePrivilege.objects.filter(user=user, slice=slice)
        assert(len(dps) == 1)

    def create_slice_nocreate(self):
        self.assert_noobj(Slice, "testsite_testslice")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testsite_testslice", "tosca.nodes.Slice",
                                            reqs=[("testsite", "tosca.relationships.MemberOfSite")],
                                            props={"no-create": True}))
        self.assert_noobj(Slice, "testsite_testslice")

    def update_slice(self):
        self.assert_noobj(Slice, "testsite_testslice")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testsite_testslice", "tosca.nodes.Slice",
                                            reqs=[("testsite", "tosca.relationships.MemberOfSite")]))
        orig_slice = self.assert_obj(Slice, "testsite_testslice", enabled=True, description="", slice_url="", max_instances=10)
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testsite_testslice", "tosca.nodes.Slice",
                                            reqs=[("testsite", "tosca.relationships.MemberOfSite")],
                                            props={"description": "foo"}))
        slice = self.assert_obj(Slice, "testsite_testslice", enabled=True, description="foo", slice_url="", max_instances=10)
        assert(orig_slice.id == slice.id)

    def update_slice_noupdate(self):
        self.assert_noobj(Slice, "testsite_testslice")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testsite_testslice", "tosca.nodes.Slice",
                                            reqs=[("testsite", "tosca.relationships.MemberOfSite")]))
        orig_slice = self.assert_obj(Slice, "testsite_testslice", enabled=True, description="", slice_url="", max_instances=10)
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testsite_testslice", "tosca.nodes.Slice",
                                            reqs=[("testsite", "tosca.relationships.MemberOfSite")],
                                            props={"description": "foo",
                                                   "no-update": True}))
        slice = self.assert_obj(Slice, "testsite_testslice", enabled=True, description="", slice_url="", max_instances=10)
        assert(orig_slice.id == slice.id)

    def destroy_slice(self):
        self.assert_noobj(Slice, "testsite_testslice")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testsite_testslice", "tosca.nodes.Slice",
                                            reqs=[("testsite", "tosca.relationships.MemberOfSite")]))
        self.assert_obj(Slice, "testsite_testslice", enabled=True, description="", slice_url="", max_instances=10)
        self.destroy(self.get_base_templates() +
                     self.make_nodetemplate("testsite_testslice", "tosca.nodes.Slice",
                                            reqs=[("testsite", "tosca.relationships.MemberOfSite")]))
        self.assert_noobj(Slice, "testsite_testslice")

    def destroy_slice_nodelete(self):
        self.assert_noobj(Slice, "testsite_testslice")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testsite_testslice", "tosca.nodes.Slice",
                                            reqs=[("testsite", "tosca.relationships.MemberOfSite")]))
        orig_slice = self.assert_obj(Slice, "testsite_testslice", enabled=True, description="", slice_url="", max_instances=10)
        self.destroy(self.get_base_templates() +
                     self.make_nodetemplate("testsite_testslice", "tosca.nodes.Slice",
                                            reqs=[("testsite", "tosca.relationships.MemberOfSite")],
                                            props={"no-delete": True}))
        slice = self.assert_obj(Slice, "testsite_testslice", enabled=True, description="", slice_url="", max_instances=10)
        assert(slice.id == orig_slice.id)

if __name__ == "__main__":
    SliceTest()


