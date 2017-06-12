def can_update(self, user):
    return user.can_update_deployment(self)

@staticmethod
def select_by_user(user):
    from core.models.deploymentprivilege import DeploymentPrivilege
    if user.is_admin:
        qs = DeploymentPrivilege.objects.all()
    else:
        dpriv_ids = [dp.id for dp in DeploymentPrivilege.objects.filter(user=user)]
        qs = DeploymentPrivilege.objects.filter(id__in=dpriv_ids)
    return qs
