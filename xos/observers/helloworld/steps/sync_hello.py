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
        instance = record.instance_backref        
        instance.userData="packages:\n  - apache2\nruncmd:\n  - update-rc.d apache2 enable\n  - service apache2 start\nwrite_files:\n-   content: Hello %s\n    path: /var/www/html/hello.txt"%record.name
        instance.save()
        
    def delete_record(self, m):
        return
