def __unicode__(self):  return u'%s' % (self.name)

def save(self, *args, **kwds):
    if (not self.subnet) and (NO_OBSERVER):
        from util.network_subnet_allocator import find_unused_subnet
        self.subnet = find_unused_subnet(existing_subnets=[x.subnet for x in Network.objects.all()])
        print "DEF_MOD_NET_IP", self.start_ip
    super(Network, self).save(*args, **kwds)

def can_update(self, user):
    return user.can_update_slice(self.owner)

@property
def nat_list(self):
    return ParseNatList(self.ports)

@staticmethod
def select_by_user(user):
    if user.is_admin:
        qs = Network.objects.all()
    else:
        slices = Slice.select_by_user(user)
        #slice_ids = [s.id for s in Slice.select_by_user(user)]
        qs = Network.objects.filter(owner__in=slices)
    return qs

def get_parameters(self):
    # returns parameters from the template, updated by self.
    p={}
    if self.template:
        p = self.template.get_parameters()
    p.update(ParameterMixin.get_parameters(self))
    return p

