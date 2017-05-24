def get_acl(self):
    return AccessControlList(self.accessControl)

def test_acl(self, slice=None, user=None):
    potential_users=[]

    if user:
        potential_users.append(user)

    if slice:
        potential_users.append(slice.creator)
        for priv in slice.sliceprivileges.all():
            if priv.user not in potential_users:
                potential_users.append(priv.user)

    acl = self.get_acl()
    for user in potential_users:
        if acl.test(user) == "allow":
            return True

    return False

@staticmethod
def select_by_acl(user):
    ids = []
    for deployment in Deployment.objects.all():
        acl = deployment.get_acl()
        if acl.test(user) == "allow":
            ids.append(deployment.id)

    return Deployment.objects.filter(id__in=ids)

def can_update(self, user):
    return user.can_update_deployment(self)

