@staticmethod
def select_by_user(user):
    if user.is_admin:
        qs = Controller.objects.all()
    else:
        from core.models.privilege import Privilege
        deployments = [dp.deployment for dp in Privilege.objects.filter(accessor_id=user_id, accessor_type='User', permission__in=['role:Admin', 'role:admin'])]
        qs = Controller.objects.filter(deployment__in=deployments)
    return qs
