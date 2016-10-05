from xosresource import XOSResource
from core.models import NodeLabel

class XOSNodeLabel(XOSResource):
    provides = "tosca.nodes.NodeLabel"
    xos_model = NodeLabel

