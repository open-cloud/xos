import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import sys
from optparse import OptionParser
from getpass import getpass
import xmlrpclib
from plclassic.site_importer import SiteImporter
from plclassic.user_importer import UserImporter
from plclassic.slice_importer import SliceImporter
from plclassic.instance_importer import InstanceImporter


class Call:
    def __init__(self, callable, auth):
        self.callable = callable
        self.auth = auth

    def __call__(self, *args, **kwds):
        a = [self.auth] + list(args)
        return self.callable(*a)

class API():
    def __init__(self, username, password, url):
        self.auth = {'AuthMethod': 'password',
                     'Username': username,
                     'AuthString': password}
        self.server = xmlrpclib.ServerProxy(url, allow_none=True)

    def __getattr__(self, name):         
        return Call(getattr(self.server, name), self.auth) 

class Importer: 

    def __init__(self, username, password, url):
        api = API(username, password, url)
        self.sites = SiteImporter(api)
        self.slices = SliceImporter(api)
        self.users = UserImporter(api)
        self.instances = InstanceImporter(api)

    def run(self):
        self.sites.run()
        self.users.run()
        self.slices.run(remote_sites=self.sites.remote_sites, 
                        local_sites=self.sites.local_sites)
        self.instances.run()           



if __name__ == '__main__':
    parser = OptionParser()
        
    parser.add_option("-u", "--username", dest="username",
                        help="PLC username with which to authenticate")
    parser.add_option("", "--url", dest="url",
                        help="PLC url to contact")

    (config, args) = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    password = None
    try:
        password = getpass()
    except (EOFError, KeyboardInterrupt):
        print
        sys.exit(0)

    Importer(config.username, password, config.url).run()
