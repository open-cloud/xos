KIND="generic"

def __init__(self, *args, **kwargs):
    # for subclasses, set the default kind appropriately
    self._meta.get_field("kind").default = self.KIND
    super(TenantRoot, self).__init__(*args, **kwargs)

def get_subscribed_tenants(self, tenant_class):
    ids = self.subscribed_tenants.filter(kind=tenant_class.KIND)
    return tenant_class.objects.filter(id__in=ids)

def get_newest_subscribed_tenant(self, kind):
    st = list(self.get_subscribed_tenants(kind))
    if not st:
        return None
    return sorted(st, key=attrgetter('id'))[0]

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

