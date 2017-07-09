def can_update(self, user):
    if user.is_readonly:
        return False
    if user.is_admin:
        return True

    cprivs = ControllerPrivilege.objects.filter(privilege__accessor_id=user.id, privilege__object_type='Site')
    for cpriv in cprivs:
        if cpriv.privilege.permission in ['role:admin', 'role:Admin']:
            return True
    return False

@staticmethod
def select_by_user(user):
    if user.is_admin:
        qs = ControllerPrivilege.objects.filter(privilege__object_type='Site')
    else:
        cpriv_ids = [cp.id for cp in ControllerPrivilege.objects.filter(privilege__accessor_id=user.id, privilege__object_type='Site')]
        qs = ControllerPrivilege.objects.filter(id__in=cpriv_ids, privilege__object_type='Site')
    return qs
