KIND="coarse"

def save(self, *args, **kwargs):
    if (not self.subscriber_service):
        raise XOSValidationError("subscriber_service cannot be null")
    if (self.subscriber_tenant or self.subscriber_user):
        raise XOSValidationError(
            "subscriber_tenant and subscriber_user must be null")

    super(ServiceDependency, self).save()

