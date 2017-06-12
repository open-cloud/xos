def save(self, *args, **kwds):
    if self.instance:
        slice = self.instance.slice
        if (slice not in self.network.permitted_slices.all()) and (slice != self.network.owner) and (not self.network.permit_all_slices):
            # to add a instance to the network, then one of the following must be true:
            #   1) instance's slice is in network's permittedSlices list,
            #   2) instance's slice is network's owner, or
            #   3) network's permitAllSlices is true
            raise ValueError("Slice %s is not allowed to connect to network %s" % (str(slice), str(self.network)))

    super(Port, self).save(*args, **kwds)

def can_update(self, user):
    if self.instance:
        return user.can_update_slice(self.instance.slice)
    if self.network:
        return user.can_update_slice(self.network.owner)
    return False

@staticmethod
def select_by_user(user):
    if user.is_admin:
        qs = Port.objects.all()
    else:
        instances = Instance.select_by_user(user)
        instance_ids = [instance.id for instance in instances]
        networks = Network.select_by_user(user)
        network_ids = [network.id for network in networks]
        qs = Port.objects.filter(Q(instance__in=instance_ids) | Q(network__in=network_ids))
    return qs

