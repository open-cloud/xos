import xmlrpclib
from importer.planetstack.role_importer import RoleImporter
from importer.planetstack.site_importer import SiteImporter
from importer.planetstack.user_importer import UserImporter
from importer.planetstack.slice_importer import SliceImporter
from importer.planetstack.sliver_importer import SliverImporter


class Call:
    def __init__(self, callable, auth):
        self.callable = callable
        self.auth = auth

    def __call__(self, *args, **kwds):
        a = [auth] + args
        return self.callable(*a)

class API():
    def __init__(self):
        self.auth = {}
        self.server = xmlrpclib.ServerProxy("URL", allow_none=True)

    def __getattr__(self, name):         
        return Call(getattr(self.server, name), self.auth) 

class Importer: 

    def __init__(self):
        self.api = API()
        self.roles = RoleImporter(self)
        self.sites = SiteImporter(self)
        self.users = UserImporter(self)
        self.slices = SliceImporter(self)
        self.slivers = SliverImporter(self)

    def run(self):
        self.roles.run()
        self.sites.run()
        self.users.run()
        self.slices.run()
        self.slivers.run()           


