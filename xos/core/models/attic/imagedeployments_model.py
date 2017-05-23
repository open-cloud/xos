class Meta:
    unique_together = ('image', 'deployment')

def can_update(self, user):
    return user.can_update_deployment(self.deployment)
