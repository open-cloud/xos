from django.http import HttpResponse
from monitor import driver
import json

def Stats(request):
    model = request.GET['model_name']
    pk = int(request.GET['pk'])
    meter = int(request.GET['meter'])
    
    meters = monitor.get_meters(meter, model, pk)
    return json.dumps(meters)
