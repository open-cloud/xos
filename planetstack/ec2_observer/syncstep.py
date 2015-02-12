import os
import base64
from datetime import datetime
from xos.config import Config
from util.logger import Logger, logging
from observer.steps import *

logger = Logger(level=logging.INFO)

class FailedDependency(Exception):
    pass

class SyncStep:
    """ A PlanetStack Sync step. 

    Attributes:
        psmodel        Model name the step synchronizes 
        dependencies    list of names of models that must be synchronized first if the current model depends on them
    """ 
    slow=False
    def get_prop(prop):
        try:
            sync_config_dir = Config().sync_config_dir
        except:
            sync_config_dir = '/etc/planetstack/sync'
        prop_config_path = '/'.join(sync_config_dir,self.name,prop)
        return open(prop_config_path).read().rstrip()

    def __init__(self, **args):
        """Initialize a sync step
           Keyword arguments:
                   name -- Name of the step
                provides -- PlanetStack models sync'd by this step
        """
        dependencies = []
        self.driver = args.get('driver')
        self.error_map = args.get('error_map')

        try:
            self.soft_deadline = int(self.get_prop('soft_deadline_seconds'))
        except:
            self.soft_deadline = 5 # 5 seconds

        return

    def fetch_pending(self, deletion=False):
        # This is the most common implementation of fetch_pending
        # Steps should override it if they have their own logic
        # for figuring out what objects are outstanding.
        main_obj = self.provides[0]
        if (not deleted):
            objs = main_obj.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        else:
            objs = main_obj.deleted_objects.all()

        return objs
        #return Sliver.objects.filter(ip=None)
    
    def check_dependencies(self, obj, failed):
        for dep in self.dependencies:
            peer_name = dep[0].lower() + dep[1:]    # django names are camelCased with the first letter lower
            peer_object = getattr(obj, peer_name)
            
            # peer_object can be None, and if so there
            # is no object-level dependency
            if (peer_object and peer_object.pk==failed.pk):
                raise FailedDependency

    def call(self, failed=[], deletion=False):
        pending = self.fetch_pending(deletion)
        for o in pending:
            try:
                for f in failed:
                    self.check_dependencies(o,f) # Raises exception if failed
                if (deletion):
                    self.delete_record(o)
                    o.delete(purge=True)
                else:
                    self.sync_record(o)
                    o.enacted = datetime.now() # Is this the same timezone? XXX
                    o.backend_status = "OK"
                    o.save(update_fields=['enacted'])
            except Exception,e:
                try:
                    o.backend_status = self.error_map.map(str(e))
                except:
                    o.backend_status = str(e)

                if (o.pk):
                    o.save(update_fields=['backend_status'])

                logger.log_exc("sync step failed!")
                failed.append(o)

        return failed

    def __call__(self, **args):
        return self.call(**args)
