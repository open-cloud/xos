from xosresource import XOSResource
from core.models import Service,User,ServiceDependency,AddressPool

class XOSService(XOSResource):
    provides = "tosca.nodes.Service"
    xos_model = Service
    copyin_props = ["view_url", "icon_url", "kind", "enabled", "published", "public_key", "private_key_fn", "versionNumber"]

    def postprocess(self, obj):
        for provider_service_name in self.get_requirements("tosca.relationships.TenantOfService"):
            provider_service = self.get_xos_object(Service, name=provider_service_name)

            existing_tenancy = ServiceDependency.objects.filter(provider_service = provider_service, subscriber_service = obj)
            if existing_tenancy:
                self.info("Tenancy relationship from %s to %s already exists" % (str(obj), str(provider_service)))
            else:
                tenancy = ServiceDependency(provider_service = provider_service,
                                       subscriber_service = obj)
                tenancy.save()

                self.info("Created Tenancy relationship  from %s to %s" % (str(obj), str(provider_service)))

        for ap_name in self.get_requirements("tosca.relationships.ProvidesAddresses"):
            ap = self.get_xos_object(AddressPool, name=ap_name)
            ap.service = obj
            ap.save()

    def can_delete(self, obj):
        if obj.slices.exists():
            self.info("Service %s has active slices; skipping delete" % obj.name)
            return False
        return super(XOSService, self).can_delete(obj)

