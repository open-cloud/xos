from xosresource import XOSResource
from core.models import Subscriber

class XOSSubscriber(XOSResource):
    provides = "tosca.nodes.Subscriber"
    xos_model = Subscriber
    copyin_props = ["service_specific_id"]

    def postprocess(self, obj):
        pass

    def can_delete(self, obj):
        return super(XOSService, self).can_delete(obj)

