#!/usr/bin/env python

import os
import sys
import base64
import traceback
from django.db.models import F, Q
from xos.config import Config, XOS_DIR
from synchronizers.base.syncstep import SyncStep
from core.models import Service
from services.requestrouter.models import ServiceMap
from xos.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from rrlib import RequestRouterLibrary
from configurationPush import ConfigurationPush
import rrlib_config

logger = Logger(level=logging.INFO)

class SyncServiceMap(SyncStep, RequestRouterLibrary, ConfigurationPush):
    provides=[ServiceMap]
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
	RequestRouterLibrary.__init__(self)
	ConfigurationPush.__init__(self)

    def fetch_pending(self):
	try:
        	ret = ServiceMap.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        	return ret
	except Exception, e:
        	traceback.print_exc()
            	return None

    def sync_record(self, servicemap):
	try:
		print "sync! %s " % self.get_servicemap_uid(servicemap)
		self.gen_dnsredir_serviceconf(servicemap)
		self.gen_dnsdemux_serviceconf(servicemap)
        	# push generated files from temp_config
		service_uid = self.get_servicemap_uid(servicemap)
		self.config_push(service_uid, rrlib_config.REDIR_USER, XOS_DIR + "/observers/requestrouter/playbook/site_redir.yml", "/etc/ansible/requestrouter/dnsredir/hosts")
		self.config_push(service_uid, rrlib_config.DEMUX_USER, XOS_DIR + "/observers/requestrouter/playbook/site_demux.yml", "/etc/ansible/requestrouter/dnsdemux/hosts")
		self.teardown_temp_configfiles(service_uid)
	except Exception, e:
                traceback.print_exc()
                return False

if __name__ == "__main__":
    sv = SyncServiceMap()

    recs = sv.fetch_pending()

    for rec in recs:
        sv.sync_record( rec )
