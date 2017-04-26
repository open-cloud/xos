objects = ControllerLinkManager()
deleted_objects = ControllerLinkDeletionManager()

class Meta:
    unique_together = ('site', 'deployment', 'controller')

def __unicode__(self):  return u'%s %s' % (self.deployment, self.site)
