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

