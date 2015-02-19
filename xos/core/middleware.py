from threading import local

_active = local()

def get_request():
    if not hasattr(_active, "request"):
        raise Exception("Please add 'core.middleware.GlobalRequestMiddleware' to <XOS_DIR>/xos.settings.py:MIDDLEWARE_CLASSES")
    return _active.request

class GlobalRequestMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        _active.request = request
        return None
