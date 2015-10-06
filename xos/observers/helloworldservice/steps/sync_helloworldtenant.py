import os
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from observer.syncstep import SyncStep
from helloworldservice.models import HelloWorldService,HelloWorldTenant
from observers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from util.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncHelloWorldServiceTenant(SyncStep):
    provides=[HelloWorldTenant]
    observes=HelloWorldTenant
    requested_interval=1
    
    def sync_record(self, record):
	logger.info("Syncing helloworldtenant");
        open('log','w').write(record.name)
        
    def delete_record(self, m):
        return
