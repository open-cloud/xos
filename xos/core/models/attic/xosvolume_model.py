def __unicode__(self): return u'%s' % (self.container_path)

def save(self, *args, **kwargs):
   super(XOSVolume, self).save(*args, **kwargs)

   # This is necessary, as the XOS syncstep handles rerunning the docker-
   # compose.
   # TODO: Update onboarding synchronizer and replace this with watcher functionality
   if self.xos:
       # force XOS to rebuild
       self.xos.save(update_fields=["updated"])
