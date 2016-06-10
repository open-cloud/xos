#!/usr/bin/env python                                                                                                               

import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import XOS
django.setup()

xoses = XOS.objects.all()
if not xoses:
    print "There is no XOS model"

for xos in xoses:
    xos.rebuild()

