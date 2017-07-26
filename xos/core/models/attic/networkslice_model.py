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

