import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
django.setup()

def purge(cls):
    for obj in cls.deleted_objects.all():
        obj.delete(purge=True)

for model in [Instance, Slice, Site, Service, User, Image, ImageDeployments, Port]:
    purge(model)
