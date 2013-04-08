import ast

def parse_request(request):
    d = {}
    for (k,v) in request.items():
        d[k] = ast.literal_eval(v) 
    return d
