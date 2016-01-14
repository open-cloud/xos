#!/usr/bin/env python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
from synchronizers.base.backend import Backend 

if __name__ == '__main__':

    backend = Backend()
    backend.run()
 
