def can_update(self, user):
    return user.can_update_slice(self.slice)

@staticmethod
def select_by_user(user):
    if user.is_admin:
        qs = SliceTag.objects.all()
    else:
        slices = Slice.select_by_user(user)
        qs = SliceTag.objects.filter(slice__in=slices)
    return qs
