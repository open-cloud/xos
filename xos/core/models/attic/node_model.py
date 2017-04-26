def __unicode__(self):  return u'%s' % (self.name)

def __init__(self, *args, **kwargs):
    super(Node, self).__init__(*args, **kwargs)
    self.no_sync=True

def can_update(self, user):
    return user.can_update_site(self.site, allow=['tech'])

def save(self, *args, **kwds):
    if self.site is None and self.site_deployment is not None:
        self.site = self.site_deployment.site

    super(Node, self).save(*args, **kwds)
