KIND="coarse"

def save(self, *args, **kwargs):
    if (not self.subscriber_service):
        raise XOSValidationError("subscriber_service cannot be null", {'subscriber service' : 'subscriber_service cannot be null'})
    if (self.subscriber_tenant):
        raise XOSValidationError("subscriber_tenant must be null", {'subscriber tenant' : 'subscriber_tenant must be null'})
    if (self.subscriber_user):
        raise XOSValidationError("subscriber_user must be null", {'subscriber user' : 'subscriber_user must be null'})


    super(ServiceDependency, self).save()

