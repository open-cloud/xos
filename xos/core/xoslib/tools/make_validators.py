import os
import sys
XOS_DIR="/opt/xos"
os.chdir(XOS_DIR)
sys.path.append(XOS_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
import core.models
from django.db import models
django.setup()
from django.forms.models import model_to_dict
import inspect
from django.core import serializers
import json

print "function xos_get_validators() {"

for c in dir(core.models):
    c = getattr(core.models,c)
    if inspect.isclass(c) and issubclass(c, models.Model):
        c=c()
        classname = c.__class__.__name__
        classname = classname[0].lower() + classname[1:]

        if (classname in ["plCoreBase", "singletonModel"]):
            continue

        fields = c.getValidators();

        fields_json = json.dumps(fields)

        print "  this." + classname + " = " + fields_json + ";"

print "};"
print "xosvalidators = new xos_get_validators();"

