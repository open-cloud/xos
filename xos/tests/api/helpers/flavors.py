import dredd_hooks as hooks
import sys

# HELPERS
# NOTE move in separated module
import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
import urllib2
import json
django.setup()

def createFlavor():
    fl = Flavor(id=1)
    fl.name = 'm1.large'
    fl.save()
    print(fl, fl.id)

createFlavor()