import json

def parse_request(request):
    d = {}
    for (k,v) in request.items():
        d[k] = json.loads(v) 

