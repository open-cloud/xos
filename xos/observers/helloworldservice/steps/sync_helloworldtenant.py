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

class SyncHelloWorldServiceTenant(SyncInstanceUsingAnsible):
    provides=[HelloWorldTenant]
    observes=HelloWorldTenant
    requested_interval=0
    template_name = "test.yaml"
    service_key_name = "/opt/xos/observers/helloworldservice/helloworldservice_private_key"
    
    def get_extra_attributes(self, o):
	return {"display_message": o.display_message}

    def delete_record(self, m):
        return
