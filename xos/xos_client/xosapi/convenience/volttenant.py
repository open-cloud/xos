from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperVOLTTenant(ORMWrapper):
    @property
    def vcpe(self):
        links = self.stub.ServiceInstanceLink.objects.filter(subscriber_service_instance_id = self.id)
        for link in links:
            # cast from ServiceInstance to VSGTenant
            vsgs = self.stub.VSGTenant.objects.filter(id = link.provider_service_instance.id)
            if vsgs:
                return vsgs[0]
        return None

    @property
    def subscriber(self):
        links = self.stub.ServiceInstanceLink.objects.filter(provider_service_instance_id = self.id)
        for link in links:
            subs = self.stub.CordSubscriberRoot.objects.filter(id=link.subscriber_service_instance_id)
            if subs:
                return subs[0]
        return None

register_convenience_wrapper("VOLTTenant", ORMWrapperVOLTTenant)
