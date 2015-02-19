import ast
from django.http.request import QueryDict

def parse_request(request):
    d = {}
    if isinstance(request, unicode):
        d = ast.literal_eval(request)
    elif isinstance(request, QueryDict):
        for (k,v) in request.items():
            d[k] = ast.literal_eval(v)
    elif isinstance(request, dict):
        d = request    

    return d
