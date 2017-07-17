def __init__(self, *args, **kwargs):
    super(ServiceInstance, self).__init__(*args, **kwargs)

@property
def tenantattribute_dict(self):
    attrs = {}
    for attr in self.tenantattributes.all():
        attrs[attr.name] = attr.value
    return attrs

# helper function to be used in subclasses that want to ensure
# service_specific_id is unique

def validate_unique_service_specific_id(self, none_okay=False):
    if not none_okay and (self.service_specific_id is None):
        raise XOSMissingField("subscriber_specific_id is None, and it's a required field", fields={
                              "service_specific_id": "cannot be none"})

    if self.service_specific_id:
        conflicts = self.__class__.objects.filter(
            service_specific_id=self.service_specific_id)
        if self.pk:
            conflicts = conflicts.exclude(pk=self.pk)
        if conflicts:
            raise XOSDuplicateKey("service_specific_id %s already exists" % self.service_specific_id, fields={
                                  "service_specific_id": "duplicate key"})

def get_subscribed_tenants(self, tenant_class):
    """ Return all ServiceInstances of class tenant_class that have a link to this ServiceInstance """
    results=[]
    # TODO: Make query more efficient
    for si in tenant_class.objects.all():
        for link in si.subscribed_links.all():
            if link.provider_service_instance == self:
                results.append(si)
    return results

def get_newest_subscribed_tenant(self, kind):
    st = list(self.get_subscribed_tenants(kind))
    if not st:
        return None
    return sorted(st, key=attrgetter('id'))[0]

