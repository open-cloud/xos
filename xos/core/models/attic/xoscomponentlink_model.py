def save(self, *args, **kwds):
    # If this is a new object, then check to make sure it doesn't already exist
    if not self.pk:
        existing = XOSComponentLink.objects.filter(container=self.container, alias=self.alias)
        if len(existing) > 0:
            raise XOSValidationError('XOSComponentLink for %s:%s already defined' % (self.container, self.alias))
    super(XOSComponentLink, self).save(*args, **kwds)
