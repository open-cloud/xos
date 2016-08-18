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


def createSite():
    site = Site(id=1)
    site.name = 'mysite'
    site.save()
    print(site, site.id)

createSite()