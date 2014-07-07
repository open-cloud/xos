from core.models import Sliver
from xosbase import XOSBase
from django.forms.models import model_to_dict

class XOSSlivers(XOSBase):
    name = "slivers"

    def __init__(self):
         super(XOSSlivers, self).__init__()

    def get(self):
        allSlivers = list(Sliver.objects.all())

        result = []
        for sliver in allSlivers:
            d=model_to_dict(sliver)
            result.append(self.ensure_serializable(d))

        return result

