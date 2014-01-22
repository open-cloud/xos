import os
import sys
from hpc.models import ServiceProvider, ContentProvider, CDNPrefix
from observer.deleter import Deleter

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from hpclib import HpcLibrary

class ContentProviderDeleter(Deleter, HpcLibrary):
        model='ContentProvider'

        def __init__(self, **args):
            Deleter.__init__(self, **args)
            HpcLibrary.__init__(self)

        def call(self, pk, model_dict):
            print "XXX delete content provider", model_dict
            self.client.onev.Delete("ContentProvider", int(model_dict["content_provider_id"]))

