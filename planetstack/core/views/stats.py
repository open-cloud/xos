from django.http import HttpResponse
from monitor import driver
import json

def Stats(request):
    model = request.GET['model_name']
    pk = int(request.GET['pk'])
    meter = request.GET['meter']
    controller_name = request.GET['controller_name']
    
    meters = driver.get_meter(meter, model, pk)
    return HttpResponse(json.dumps(meters))
