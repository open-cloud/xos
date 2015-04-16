from core.models import Slice, SlicePrivilege, SliceRole, Sliver, Site, Node, User
from cord.models import VOLTTenant
from plus import PlusObjectMixin
from operator import itemgetter, attrgetter
from rest_framework.exceptions import APIException

class CordSubscriber(VOLTTenant, PlusObjectMixin):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(VOLTTenant, self).__init__(*args, **kwargs)

    @property
    def vcpe_id(self):
        if self.vcpe:
            return self.vcpe.id
        else:
            return None

    @vcpe_id.setter
    def vcpe_id(self, value):
        pass

    @property
    def sliver_id(self):
        if self.vcpe and self.vcpe.sliver:
            return self.vcpe.sliver.id
        else:
            return None

    @sliver_id.setter
    def sliver_id(self, value):
        pass

    @property
    def firewall_enable(self):
        if self.vcpe:
            return self.vcpe.firewall_enable
        else:
            return None

    @firewall_enable.setter
    def firewall_enable(self, value):
        if self.vcpe:
            self.vcpe.firewall_enable = value
            # TODO: save it





