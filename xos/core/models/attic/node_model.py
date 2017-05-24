def can_update(self, user):
    return user.can_update_site(self.site_deployment.site, allow=['tech'])

