@staticmethod
def select_by_user(user):

    if user.is_admin:
        qs = Controller.objects.all()
    else:
        from core.models.deploymentprivilege import DeploymentPrivilege
        deployments = [dp.deployment for dp in DeploymentPrivilege.objects.filter(user=user, role__role__in=['Admin', 'admin'])]
        qs = Controller.objects.filter(deployment__in=deployments)
    return qs
