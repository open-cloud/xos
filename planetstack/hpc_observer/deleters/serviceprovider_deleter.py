import os
import sys
from hpc.models import ServiceProvider, ContentProvider, CDNPrefix
from observer.deleter import Deleter

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from hpclib import HpcLibrary

class ServiceProviderDeleter(Deleter, HpcLibrary):
        model='ServiceProvider'

        def __init__(self, **args):
            Deleter.__init__(self, **args)
            HpcLibrary.__init__(self)

        def call(self, pk, model_dict):
            print "XXX delete service provider", model_dict
            self.client.onev.Delete("ServiceProvider", int(model_dict["service_provider_id"]))

