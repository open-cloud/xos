import os
import xmlrpclib
from plstackapi.importer.plclassic.site_importer import SiteImporter
from plstackapi.importer.plclassic.user_importer import UserImporter
from plstackapi.importer.plclassic.slice_importer import SliceImporter
from plstackapi.importer.plclassic.sliver_importer import SliverImporter


class Call:
    def __init__(self, callable, auth):
        self.callable = callable
        self.auth = auth

    def __call__(self, *args, **kwds):
        a = [auth] + args
        return self.callable(*a)

class API():
    def __init__(self):
        self.auth = {'AuthMethod': 'password',
                     'Username': None,
                     'AuthString': None}
        self.server = xmlrpclib.ServerProxy("URL", allow_none=True)

    def __getattr__(self, name):         
        return Call(getattr(self.server, name), self.auth) 

class Importer: 

    def __init__(self):
        api = API()
        self.sites = SiteImporter(api)
        self.slices = SliceImporter(api, remote_sites=self.sites.remote_sites, local_sites=self.sites.local_sites)
        self.users = UserImporter(api)
        self.slivers = SliverImporter(api)

    def run(self):
        self.roles.run()
        self.sites.run()
        self.users.run()
        self.slices.run()
        self.slivers.run()           



if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plstackapi.planetstack.settings")
    Importer().run()
