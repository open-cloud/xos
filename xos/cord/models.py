from django.db import models
from core.models import Service, PlCoreBase, Slice, Sliver, Tenant, Node, Image
from core.models.plcorebase import StrippedCharField
import os
from django.db import models
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller

"""
import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
from hpc.models import *
from cord.models import *
django.setup()
svc = Service.objects.get(name="VCPE")

t = VCPETenant(provider_service=svc)
t.caller = User.objects.all()[0]
t.save()

for v in VCPETenant.objects.all():
    v.caller = User.objects.all()[0]
    v.delete()
"""

class ConfigurationError(Exception):
    pass

class VCPEService(Service):
    class Meta:
        app_label = "vCPE"
        verbose_name = "vCPE Service"

class VCPETenant(Tenant):
    class Meta:
        proxy = True

    default_attributes = {"firewall_enable": False,
                          "sliver_id": None}

    @property
    def image(self):
        # TODO: logic to pick an image based on the feature set
        #    just use Ubuntu 14.04 for now...
        return Image.objects.get(name="Ubuntu 14.04 LTS")

    @property
    def sliver(self):
        sliver_id=self.get_attribute("sliver_id")
        if not sliver_id:
            return None
        slivers=Sliver.objects.filter(id=sliver_id)
        if not slivers:
            return None
        return slivers[0]

    @sliver.setter
    def sliver(self, value):
        if value:
            self.set_attribute("sliver_id", value.id)
        else:
            self.set_attribute("sliver_id", None)

    @property
    def firewall_enable(self):
        return self.get_attribute("firewall_enable", self.default_attributes["firewall_enable"])

    @firewall_enable.setter
    def firewall_enable(self, value):
        self.set_attribute("firewall_enable", value)

    def pick_node(self):
        nodes = list(Node.objects.all())
        # TODO: logic to filter nodes by which nodes are up, and which
        #   nodes the slice can instantiate on.
        nodes = sorted(nodes, key=lambda node: node.slivers.all().count())
        return nodes[0]

    def manage_sliver(self):
        if self.deleted:
            return

        # TODO: This could be a model_policy...
        if (self.sliver is not None) and (self.sliver.image != self.image):
            self.sliver.delete()
            self.sliver = None
        if self.sliver is None:
            if not self.provider_service.slices.count():
                raise ConfigurationError("The VCPE service has no slicers")

            node =self.pick_node()
            sliver = Sliver(slice = self.provider_service.slices.all()[0],
                            node = node,
                            image = self.image,
                            creator = self.caller,
                            deployment = node.site_deployment.deployment)
            sliver.save()

            self.sliver = sliver

    def cleanup_sliver(self):
        if self.sliver:
            self.sliver.delete()
            self.sliver = None

    def save(self, *args, **kwargs):
        if not getattr(self, "caller", None):
            raise TypeError("VCPETenant's self.caller was not set")
        self.manage_sliver()
        super(VCPETenant, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.cleanup_sliver()
        super(VCPETenant, self).delete(*args, **kwargs)

