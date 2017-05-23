def can_update(self, user):
    return user.can_update_site(self, allow=['pi'])


