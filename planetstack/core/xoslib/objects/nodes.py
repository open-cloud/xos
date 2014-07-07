from core.models import Node
from xosbase import XOSBase
from django.forms.models import model_to_dict

class XOSNodes(XOSBase):
    name = "nodes"

    def __init__(self):
         super(XOSNodes, self).__init__()

    def get(self):
        allNodes = list(Node.objects.all())

        result = []
        for nocd in allNodes:
            d=model_to_dict(nocd)
            result.append(self.ensure_serializable(d))

        return result
