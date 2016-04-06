import os
import sys
import base64
import traceback
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from core.models import Service
from services.requestrouter.models import RequestRouterService
from xos.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from rrlib import RequestRouterLibrary

logger = Logger(level=logging.INFO)

class SyncRequestRouterService(SyncStep, RequestRouterLibrary):
    provides=[RequestRouterService]
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        RequestRouterLibrary.__init__(self)

    def fetch_pending(self):
	try:
        	ret = RequestRouterService.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        	return ret
	except Exception, e:
        	traceback.print_exc()
            	return None	

    def sync_record(self, rr_service):
	try:
        	print "syncing service!"
        	logger.info("sync'ing rr_service %s" % str(rr_service),extra=rr_service.tologdict())
        	self.gen_slice_file(rr_service)
        	rr_service.save()
		return True
	except Exception, e:
                traceback.print_exc()
                return False


