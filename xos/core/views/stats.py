from django.http import HttpResponse
from monitor import driver
from core.models import *
import json

def Stats(request):
    model = request.GET['model_name']
    pk = int(request.GET['pk'])
    meter = request.GET['meter']
    controller_name = request.GET['controller_name']
    
    controller = Controller.objects.filter(name=controller_name)

    if len(controller)==0:
        return HttpResponse(json.dumps({"stat_list": [], "error": "not found"}))

    controller=controller[0]
    keystone = {'username':controller.admin_user, 'password':controller.admin_password, 'tenant_name':controller.admin_tenant, 'auth_url':controller.auth_url, 'cacert':'/etc/ssl/certs/ca-certificates.crt'}

    for k,v in keystone.items():
        keystone['os_'+k] = v

    meters = driver.get_meter(meter, model, pk, keystone)
    return HttpResponse(json.dumps(meters))
