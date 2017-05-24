def can_update(self, user):
    return user.can_update_slice(self.owner)

@staticmethod
def select_by_user(user):
    if user.is_admin:
        qs = Network.objects.all()
    else:
        slices = Slice.select_by_user(user)
        #slice_ids = [s.id for s in Slice.select_by_user(user)]
        qs = Network.objects.filter(owner__in=slices)
    return qs


