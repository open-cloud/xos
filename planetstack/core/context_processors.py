from django.conf import settings

print dir(settings)

def planetstack(request):
    return {"DISABLE_MINIDASHBOARD": settings.DISABLE_MINIDASHBOARD}
