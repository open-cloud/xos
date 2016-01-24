import os
import sys
import traceback
from services.requestrouter.models import ServiceMap
from synchronizers.base.deleter import Deleter
from xos.logger import Logger, logging
from xos.config import Config, XOS_DIR

parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from rrlib import RequestRouterLibrary
from configurationPush import ConfigurationPush
import rrlib_config

logger = Logger(level=logging.INFO)

class ServiceMapDeleter(Deleter, RequestRouterLibrary, ConfigurationPush):
        model='ServiceMap'

        def __init__(self, **args):
            Deleter.__init__(self, **args)
            RequestRouterLibrary.__init__(self)
            ConfigurationPush.__init__(self)


        def call(self, pk, model_dict):
          try:
              servicemap = ServiceMap.objects.get(pk=pk)
              service_uid = self.get_servicemap_uid(servicemap)
              self.config_push(service_uid, rrlib_config.REDIR_USER, XOS_DIR + "/observers/requestrouter/playbook/site_redir_delete.yml", "/etc/ansible/requestrouter/dnsredir/hosts")
              self.config_push(service_uid, rrlib_config.DEMUX_USER, XOS_DIR + "/observers/requestrouter/playbook/site_demux_delete.yml", "/etc/ansible/requestrouter/dnsdemux/hosts")
              print "XXX delete ServiceMap %s", servicemap.name
              return True
          except Exception, e:
              traceback.print_exc()
              logger.exception("Failed to erase map '%s'" % map_name)
              return False

if __name__ == "__main__":
  smap = ServiceMapDeleter()
  smap.call( 6, {'name': 'Service23'} )
