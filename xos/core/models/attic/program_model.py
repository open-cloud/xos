@classmethod
def select_by_user(cls, user):
    return cls.objects.all()

def __unicode__(self): return u'%s' % (self.name)

def can_update(self, user):
    return True

def save(self, *args, **kwargs):
    # set creator on first save
    if not self.owner and hasattr(self, 'caller'):
        self.owner = self.caller

    if (self.command in ["run", "destroy"]) and (self.status in ["complete", "exception"]):
        self.status = "queued"

    super(Program, self).save(*args, **kwargs)
