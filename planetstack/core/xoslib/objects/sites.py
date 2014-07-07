from core.models import Site
from xosbase import XOSBase
from django.forms.models import model_to_dict

class XOSSites(XOSBase):
    name = "sites"

    def __init__(self):
         super(XOSSites, self).__init__()

    def get(self):
        allSites = list(Site.objects.all())

        result = []
        for site in allSites:
            d=model_to_dict(site)
            result.append(self.ensure_serializable(d))

        return result

