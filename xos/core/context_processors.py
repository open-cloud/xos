from django.conf import settings
from core.models import Site


def xos(request):
    allSites = []
    for site in Site.objects.all():
        allowNewUsers = True    # replace with logic for blessing sites for registration, if necessary
        allSites.append( {"name": site.name,
                           "id": site.id,
                           "allowNewUsers": allowNewUsers} )

    return {"DISABLE_MINIDASHBOARD": settings.DISABLE_MINIDASHBOARD,
            "XOS_BRANDING_NAME": settings.XOS_BRANDING_NAME,
            "XOS_BRANDING_CSS": settings.XOS_BRANDING_CSS,
            "sites": allSites}
