def save(self, *args, **kwds):
    # If this is a new object, then check to make sure it doesn't already exist
    if not self.pk:
        existing = XOSComponentVolume.objects.filter(container_path=self.container_path, host_path=self.host_path)
        if len(existing) > 0:
            raise XOSValidationError('XOSComponentVolume for %s:%s already defined' % (self.container_path, self.host_path), {'pk' : 'XOSComponentVolume for %s:%s already defined' % (self.container_path, self.host_path)})
    super(XOSComponentVolume, self).save(*args, **kwds)

