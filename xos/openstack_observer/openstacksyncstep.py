import os
import base64
from syncstep import SyncStep

class OpenStackSyncStep(SyncStep):
    """ XOS Sync step for copying data to OpenStack 
    """ 
    
    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        return

    def __call__(self, **args):
        return self.call(**args)
