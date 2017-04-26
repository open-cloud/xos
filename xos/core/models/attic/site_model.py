objects = ControllerManager()
deleted_objects = ControllerDeletionManager()

def __unicode__(self):  return u'%s' % (self.name)

def can_update(self, user):
    return user.can_update_site(self, allow=['pi'])


