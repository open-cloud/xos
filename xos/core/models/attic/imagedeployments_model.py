class Meta:
    unique_together = ('image', 'deployment')

def __unicode__(self):  return u'%s %s' % (self.image, self.deployment)

def can_update(self, user):
    return user.can_update_deployment(self.deployment)
