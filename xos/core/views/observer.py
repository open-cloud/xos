from django.http import HttpResponse
from core.models import *
from xos.config import Config
import json
import os
import time

def Observer(request):
    try:
        observer_name = Config().observer_name
    except AttributeError:
        observer_name = 'openstack'

    diag = Diag.objects.filter(name=observer_name).first()
    if not diag:
        return HttpResponse(json.dumps({"health": ":-X", "time": time.time(), "comp": 0}))

    t = time.time()

    
    d = json.loads(diag.backend_register)

    comp = d['last_run'] + d['last_duration']*2 + 300
    if comp>t:
        d['health'] = ':-)'
    else:
        d['health'] = ':-X'
    d['time'] = t
    d['comp'] = comp

    return HttpResponse(json.dumps(d))
