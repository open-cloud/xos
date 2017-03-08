from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperVOLTTenant(ORMWrapper):
    @property
    def vcpe(self):
        vcpe_tenants = self.stub.VSGTenant.objects.filter(subscriber_tenant_id = self.id)
        if vcpe_tenants:
            return vcpe_tenants[0]
        return None


register_convenience_wrapper("VOLTTenant", ORMWrapperVOLTTenant)
