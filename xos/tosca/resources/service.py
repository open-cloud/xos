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

    def process_nodetemplate(self):
        nodetemplate = self.nodetemplate
        serviceName = nodetemplate.name

        existing_services = Service.objects.filter(name=serviceName)
        if existing_services:
            self.info("Service %s already exists" % serviceName)
            service = existing_services[0]
        else:
            service = Service(name = serviceName)
            service.caller = self.user
            service.save()

            self.info("Created Service '%s'" % (str(service), ))

        for provider_service_name in self.get_requirements("tosca.relationships.TenantOfService"):
            provider_service = self.get_xos_object(Service, name=provider_service_name)

            existing_tenancy = CoarseTenant.get_tenant_objects().filter(provider_service = provider_service, subscriber_service = service)
            if existing_tenancy:
                self.info("Tenancy relationship from %s to %s already exists" % (str(service), str(provider_service)))
            else:
                tenancy = CoarseTenant(provider_service = provider_service,
                                       subscriber_service = service)
                tenancy.save()

                self.info("Created Tenancy relationship  from %s to %s" % (str(service), str(provider_service)))

        self.resource = service

    def save(self):
        self.resource.save()

