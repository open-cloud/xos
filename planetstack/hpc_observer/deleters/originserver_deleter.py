import os
import sys
from hpc.models import ServiceProvider, ContentProvider, CDNPrefix
from observer.deleter import Deleter

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from hpclib import HpcLibrary

class OriginServerDeleter(Deleter, HpcLibrary):
        model='OriginServer'

        def __init__(self, **args):
            Deleter.__init__(self, **args)
            HpcLibrary.__init__(self)

        def call(self, pk, model_dict):
            print "XXX delete origin server", model_dict
            self.client.onev.Delete("OriginServer", int(model_dict["origin_server_id"]))

