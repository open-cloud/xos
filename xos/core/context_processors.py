
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
            "XOS_BRANDING_ICON": settings.XOS_BRANDING_ICON,
            "XOS_BRANDING_FAVICON": settings.XOS_BRANDING_FAVICON,
            "XOS_BRANDING_BG": settings.XOS_BRANDING_BG,
            "sites": allSites}
