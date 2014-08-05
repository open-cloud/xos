from django.conf import settings
from core.models import Site


def planetstack(request):
    allSites = []
    for site in Site.objects.all():
        allowNewUsers = True    # replace with logic for blessing sites for registration, if necessary
        allSites.append( {"name": site.name,
                           "id": site.id,
                           "allowNewUsers": allowNewUsers} )

    return {"DISABLE_MINIDASHBOARD": settings.DISABLE_MINIDASHBOARD,
            "sites": allSites}
