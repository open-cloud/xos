class Meta:
    unique_together = ('network', 'slice')

def save(self, *args, **kwds):
    slice = self.slice
    if (slice not in self.network.permitted_slices.all()) and (slice != self.network.owner) and (not self.network.permit_all_slices):
        # to add a instance to the network, then one of the following must be true:
        #   1) instance's slice is in network's permittedSlices list,
        #   2) instance's slice is network's owner, or
        #   3) network's permitAllSlices is true
        raise ValueError("Slice %s is not allowed to connect to network %s" % (str(slice), str(self.network)))

    super(NetworkSlice, self).save(*args, **kwds)

def can_update(self, user):
    return user.can_update_slice(self.slice)

@staticmethod
def select_by_user(user):
    if user.is_admin:
        qs = NetworkSlice.objects.all()
    else:
        slice_ids = [s.id for s in Slice.select_by_user(user)]
        network_ids = [network.id for network in Network.select_by_user(user)]
        qs = NetworkSlice.objects.filter(Q(slice__in=slice_ids) | Q(network__in=network_ids))
    return qs

