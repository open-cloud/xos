KIND="generic"

def __init__(self, *args, **kwargs):
    # for subclasses, set the default kind appropriately
    self._meta.get_field("kind").default = self.KIND
    super(Tenant, self).__init__(*args, **kwargs)

@property
def tenantattribute_dict(self):
    attrs = {}
    for attr in self.tenantattributes.all():
        attrs[attr.name] = attr.value
    return attrs

# helper function to be used in subclasses that want to ensure
# service_specific_id is unique
def validate_unique_service_specific_id(self):
    if self.pk is None:
        if self.service_specific_id is None:
            raise XOSMissingField("subscriber_specific_id is None, and it's a required field", fields={
                                  "service_specific_id": "cannot be none"})

        conflicts = self.__class__.objects.filter(
            service_specific_id=self.service_specific_id)
        if conflicts:
            raise XOSDuplicateKey("service_specific_id %s already exists" % self.service_specific_id, fields={
                                  "service_specific_id": "duplicate key"})

def __xos_save_base(self, *args, **kwargs):
    subCount = sum([1 for e in [self.subscriber_service, self.subscriber_tenant,
                                self.subscriber_user, self.subscriber_root] if e is not None])
    if (subCount > 1):
        raise XOSConflictingField(
            "Only one of subscriber_service, subscriber_tenant, subscriber_user, subscriber_root should be set")


def get_subscribed_tenants(self, tenant_class):
    ids = self.subscribed_tenants.filter(kind=tenant_class.KIND)
    return tenant_class.objects.filter(id__in=ids)

def get_newest_subscribed_tenant(self, kind):
    st = list(self.get_subscribed_tenants(kind))
    if not st:
        return None
    return sorted(st, key=attrgetter('id'))[0]

