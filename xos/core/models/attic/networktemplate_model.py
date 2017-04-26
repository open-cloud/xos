ACCESS_CHOICES = ((None, 'None'), ('indirect', 'Indirect'), ('direct', 'Direct'))

def __init__(self, *args, **kwargs):
    super(NetworkTemplate, self).__init__(*args, **kwargs)

    if (self.topology_kind=="BigSwitch"):
        print >> sys.stderr, "XXX warning: topology_kind invalid case"
        self.topology_kind="bigswitch"
    elif (self.topology_kind=="Physical"):
        print >> sys.stderr, "XXX warning: topology_kind invalid case"
        self.topology_kind="physical"
    elif (self.topology_kind=="Custom"):
        print >> sys.stderr, "XXX warning: topology_kind invalid case"
        self.toplogy_kind="custom"

def save(self, *args, **kwargs):
    self.enforce_choices(self.access, self.ACCESS_CHOICES)
    super(NetworkTemplate, self).save(*args, **kwargs)

def __unicode__(self):  return u'%s' % (self.name)

