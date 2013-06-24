#!/usr/bin/env python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
from openstack.backend import Backend 

if __name__ == '__main__':

    backend = Backend()
    backend.run()
 
