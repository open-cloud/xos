def __unicode__(self):  return u'%s' % (self.name)

def __init__(self, *args, **kwargs):
    super(XOS, self).__init__(*args, **kwargs)

def save(self, *args, **kwds):
    super(XOS, self).save(*args, **kwds)

#    def can_update(self, user):
#        return user.can_update_site(self.site, allow=['tech'])

def rebuild(self, services=[]):
    raise Exception("Not Implemented")

