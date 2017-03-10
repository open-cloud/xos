from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperVOLTTenant(ORMWrapper):
    @property
    def vcpe(self):
        vcpe_tenants = self.stub.VSGTenant.objects.filter(subscriber_tenant_id = self.id)
        if vcpe_tenants:
            return vcpe_tenants[0]
        return None

    @property
    def subscriber(self):
        if not self.subscriber_root:
            return None
        subs = self.stub.CordSubscriberRoot.objects.filter(id=self.subscriber_root.id)
        if not subs:
            return None
        return subs[0]


register_convenience_wrapper("VOLTTenant", ORMWrapperVOLTTenant)
