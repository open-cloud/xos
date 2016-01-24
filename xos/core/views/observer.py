from django.http import HttpResponse
from core.models import *
import json
import os
import time

def Observer(request):
    if not os.path.exists('/tmp/observer_last_run'):
        return HttpResponse(json.dumps({"health": ":-X", "time": time.time(), "comp": 0}))

    t = time.time()
    status_str = open('/tmp/observer_last_run','r').read()
    d = json.loads(status_str)
    comp = d['last_run'] + d['last_duration']*2 + 300
    if comp>t:
        d['health'] = ':-)'
    else:
        d['health'] = ':-X'
    d['time'] = t
    d['comp'] = comp

    return HttpResponse(json.dumps(d))
