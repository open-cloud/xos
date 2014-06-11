from django.conf import settings

def planetstack(request):
    return {"DISABLE_MINIDASHBOARD": settings.DISABLE_MINIDASHBOARD}
