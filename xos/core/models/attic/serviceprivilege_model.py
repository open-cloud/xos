class Meta:
    unique_together = ('user', 'service', 'role')

def __unicode__(self): return u'%s %s %s' % (
    self.service, self.user, self.role)

def can_update(self, user):
    if not self.service.enabled:
        raise PermissionDenied, "Cannot modify permission(s) of a disabled service"
    return self.service.can_update(user)

def save(self, *args, **kwds):
    if not self.service.enabled:
        raise PermissionDenied, "Cannot modify permission(s) of a disabled service"
    super(ServicePrivilege, self).save(*args, **kwds)

def delete(self, *args, **kwds):
    if not self.service.enabled:
        raise PermissionDenied, "Cannot modify permission(s) of a disabled service"
    super(ServicePrivilege, self).delete(*args, **kwds)

@classmethod
def select_by_user(cls, user):
    if user.is_admin:
        qs = cls.objects.all()
    else:
        qs = cls.objects.filter(user=user)
    return qs
