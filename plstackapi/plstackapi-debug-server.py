#!/usr/bin/env python
import os
import sys

from plstackapi.planetstack.config import Config 

if __name__ == '__main__':

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plstackapi.planetstack.settings")
    from django.core.management import ManagementUtility
    config = Config()
    url = "%s:%s" % (config.api_host, config.api_port)
    args = [__file__, 'runserver', url] 
    server = ManagementUtility(args)
    server.execute()
