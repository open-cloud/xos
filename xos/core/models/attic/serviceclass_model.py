class Meta(PlCoreBase.Meta):
   verbose_name_plural = "Service classes"

def __unicode__(self):  return u'%s' % (self.name)

def save_by_user(self, user, *args, **kwds):
    if self.can_update(user):
        super(ServiceClass, self).save(*args, **kwds)
