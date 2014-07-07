from core.models import Slice
from xosbase import XOSBase
from django.forms.models import model_to_dict

class XOSSlices(XOSBase):
    name = "slices"

    def __init__(self):
         super(XOSSlices, self).__init__()

    def get(self):
        allSlices = list(Slice.objects.all())

        result = []
        for slice in allSlices:
            d = model_to_dict(slice)
            result.append(self.ensure_serializable(d))

        return result


