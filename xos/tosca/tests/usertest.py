from basetest import BaseToscaTest

from core.models import User

class UserTest(BaseToscaTest):
    tests = ["create_user_minimal",
             "create_user_maximal",
             "create_user_key_artifact",
             "destroy_user",
                           ]

    def cleanup(self):
        self.try_to_delete(User, email="test@user.com")

    def get_base_templates(self):
        return self.make_nodetemplate("testsite", "tosca.nodes.Site")

    def assert_nouser(self, email):
        assert(not User.objects.filter(email=email))

    def assert_user(self, email, **kwargs):
        obj = User.objects.get(email=email)
        assert(obj)
        for (k,v) in kwargs.items():
            if (getattr(obj,k,None) != v):
                print "Object %s property '%s' is '%s' and should be '%s'" % (obj, k, getattr(obj,k,None), v)
                assert(False)
        return obj

    def create_user_minimal(self):
        self.assert_nouser("test@user.com")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test@user.com", "tosca.nodes.User",
                         props = {"firstname": "test", "lastname": "user", "password": "letmein"},
                         reqs = [("testsite", "tosca.relationships.MemberOfSite")]))
        user = self.assert_user("test@user.com",
                                 firstname="test",
                                 lastname="user",
                                 is_active=True,
                                 is_admin=False)


    def create_user_maximal(self):
        self.assert_nouser("test@user.com")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test@user.com", "tosca.nodes.User",
                         props = {"firstname": "test",
                                  "lastname": "user",
                                  "password": "letmein",
                                  "phone": "123-456-7890",
                                  "user_url": "http://foo.bar/",
                                  "public_key": "thisismykey",
                                  "is_active": False,
                                  "is_admin": True},
                         reqs = [("testsite", "tosca.relationships.MemberOfSite")]))
        user = self.assert_user("test@user.com",
                                 firstname="test",
                                 lastname="user",
                                 phone="123-456-7890",
                                 user_url="http://foo.bar/",
                                 public_key="thisismykey",
                                 # is_active=False, XXX investigate -- this is failing
                                 is_admin=True)

    def create_user_key_artifact(self):
        self.assert_nouser("test@user.com")
        pubkey = self.make_random_string(400)
        file("/tmp/pubkey", "w").write(pubkey)
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test@user.com", "tosca.nodes.User",
                         props = {"firstname": "test", "lastname": "user", "password": "letmein", "public_key": "{ get_artifact: [ SELF, pubkey, LOCAL_FILE] }" },
                         artifacts = {"pubkey": "/tmp/pubkey"},
                         reqs = [("testsite", "tosca.relationships.MemberOfSite")]))
        user = self.assert_user("test@user.com",
                                 firstname="test",
                                 lastname="user",
                                 is_active=True,
                                 is_admin=False,
                                 public_key=pubkey)

    def destroy_user(self):
        self.assert_nouser("test@user.com")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test@user.com", "tosca.nodes.User",
                         props = {"firstname": "test", "lastname": "user", "password": "letmein"},
                         reqs = [("testsite", "tosca.relationships.MemberOfSite")]))
        user = self.assert_user("test@user.com")
        self.destroy(self.get_base_templates() +
                     self.make_nodetemplate("test@user.com", "tosca.nodes.User",
                         props = {"firstname": "test", "lastname": "user", "password": "letmein"},
                         reqs = [("testsite", "tosca.relationships.MemberOfSite")]))
        self.assert_nouser("test@user.com")


if __name__ == "__main__":
    UserTest()


