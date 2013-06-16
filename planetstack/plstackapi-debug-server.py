#!/usr/bin/env python
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
from planetstack.config import Config
from openstack.backend import Backend 

if __name__ == '__main__':

    # bootstrap envirnment
    from django.core.management import ManagementUtility
    config = Config()
    url = "%s:%s" % (config.api_host, config.api_port)
    args = [__file__, 'runserver', url] 

    
    backend = Backend()
    backend.run()
 
    # start the server
    server = ManagementUtility(args)
    server.execute()
