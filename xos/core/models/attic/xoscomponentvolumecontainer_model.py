def save(self, *args, **kwds):
    # If this is a new object, then check to make sure it doesn't already exist
    if not self.pk:
        existing = XOSComponentVolumeContainer.objects.filter(name=self.name)
        if len(existing) > 0:
            raise XOSValidationError('XOSComponentVolumeContainer for %s:%s already defined' % (self.container_path, self.host_path), {'pk' : 'XOSComponentVolumeContainer for %s:%s already defined' % (self.container_path, self.host_path)})
    super(XOSComponentVolumeContainer, self).save(*args, **kwds)

