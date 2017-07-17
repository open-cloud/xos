def save(self, *args, **kwargs):
    subCount = sum([1 for e in [self.subscriber_service, self.subscriber_service_instance, self.subscriber_network] if e is not None])
    if (subCount > 1):
        raise XOSConflictingField(
            "Only one of subscriber_service, subscriber_service_instance, subscriber_network should be set")

    super(ServiceInstanceLink, self).save(*args, **kwargs)

