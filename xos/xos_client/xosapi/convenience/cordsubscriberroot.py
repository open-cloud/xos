from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperCordSubscriberRoot(ORMWrapper):
    @property
    def volt(self):
        volt_tenants = self.stub.VOLTTenant.objects.filter(subscriber_root_id = self.id)
        if volt_tenants:
            return volt_tenants[0]
        return None


register_convenience_wrapper("CordSubscriberRoot", ORMWrapperCordSubscriberRoot)
