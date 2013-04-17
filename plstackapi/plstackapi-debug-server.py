#!/usr/bin/env python
import os
import sys
import threading

from plstackapi.planetstack.config import Config 
from plstackapi.openstack.sliveragent import SliverAgent

if __name__ == '__main__':

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plstackapi.planetstack.settings")
    from django.core.management import ManagementUtility
    config = Config()
    url = "%s:%s" % (config.api_host, config.api_port)
    args = [__file__, 'runserver', url] 
    server = ManagementUtility(args)
    sliver_agent = SliverAgent()
    sliver_agent_thread = threading.Thread(target=sliver_agent.run)
    sliver_agent_thread.start()
    server.execute()
