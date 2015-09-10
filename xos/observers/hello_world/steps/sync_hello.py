import os
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from observer.syncstep import SyncStep
from helloworld.models import Hello,World
from util.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncHello(SyncStep):
    provides=[Hello]
    observes=Hello
    requested_interval=0
    
    def sync_record(self, record):
        open('/tmp/hello-synchronizer','w').write(record.name)	
        
    def delete_record(self, m):
        return
