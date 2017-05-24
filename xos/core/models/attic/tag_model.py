def can_update(self, user):
    return user.can_update_root()

@staticmethod
def select_by_user(user):
    return Tag.objects.all()
