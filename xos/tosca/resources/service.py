import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import Service,User,CoarseTenant

from xosresource import XOSResource

class XOSService(XOSResource):
    provides = "tosca.nodes.Service"
    xos_model = Service

    def get_xos_args(self):
        return {"name": self.nodetemplate.name}

    def postprocess(self, obj):
        for provider_service_name in self.get_requirements("tosca.relationships.TenantOfService"):
            provider_service = self.get_xos_object(Service, name=provider_service_name)

            existing_tenancy = CoarseTenant.get_tenant_objects().filter(provider_service = provider_service, subscriber_service = obj)
            if existing_tenancy:
                self.info("Tenancy relationship from %s to %s already exists" % (str(service), str(provider_service)))
            else:
                tenancy = CoarseTenant(provider_service = provider_service,
                                       subscriber_service = obj)
                tenancy.save()

                self.info("Created Tenancy relationship  from %s to %s" % (str(obj), str(provider_service)))

    def create(self):
        nodetemplate = self.nodetemplate

        xos_args = self.get_xos_args()
        service = Service(**xos_args)
        service.caller = self.user
        service.save()

        self.postprocess(service)

        self.info("Created Service '%s'" % (str(service), ))

    def delete(self, obj):
        if obj.slices.exists():
            self.info("Service %s has active slices; skipping delete" % obj.name)
            return
        obj.delete()

