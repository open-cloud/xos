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
        open('log','w').write(record.display_message + '\n');
	service = HelloWorldService.get_service_objects().filter(id = record.provider_service.id)[0];
	for slice in service.slices.all():
		open('log','w').write("got a slice" + '\n');
		for instance in slice.instances.all():
            		open('log','w').write("got an instance" + '\n');
            		instance.userData = "packages:\n  - apache2\nruncmd:\n  - update-rc.d apache2 enable\n  - service apache2 start\nwrite_files:\n-   content: Hello %s\n    path: /var/www/html/hello.txt"%record.display_message
            		instance.save();

    def delete_record(self, m):
        return
