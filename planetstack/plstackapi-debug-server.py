#!/usr/bin/env python
import os
import sys
import threading

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
from planetstack.config import Config 
from openstack.sliveragent import SliverAgent
from openstack.observer import OpenStackObserver

if __name__ == '__main__':

    # bootstrap envirnment
    from django.core.management import ManagementUtility
    config = Config()
    url = "%s:%s" % (config.api_host, config.api_port)
    args = [__file__, 'runserver', url] 

    
    # start the sliver agent thread
    sliver_agent = SliverAgent()
    sliver_agent_thread = threading.Thread(target=sliver_agent.run)
    sliver_agent_thread.start()

    # start the openstack observer
    observer = OpenStackObserver()
    observer_thread = threading.Thread(target=observer.run)
    observer_thread.start()

    # start the server
    server = ManagementUtility(args)
    server.execute()
