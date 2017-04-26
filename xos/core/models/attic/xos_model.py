def __unicode__(self):  return u'%s' % (self.name)

def __init__(self, *args, **kwargs):
    super(XOS, self).__init__(*args, **kwargs)

def save(self, *args, **kwds):
    super(XOS, self).save(*args, **kwds)

#    def can_update(self, user):
#        return user.can_update_site(self.site, allow=['tech'])

def rebuild(self, services=[]):
    # If `services` is empty, then only rebuild the UI
    # Otherwise, only rebuild the services listed in `services`
    with transaction.atomic():
        for loadable_module in self.loadable_modules.all():
            if (services) and (loadable_module.name not in services):
                continue
            for lmr in loadable_module.loadable_module_resources.all():
               lmr.save()
            loadable_module.save()
        self.save()
