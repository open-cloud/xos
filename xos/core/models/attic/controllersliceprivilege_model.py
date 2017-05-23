class Meta:
    unique_together = ('controller', 'slice_privilege')

def can_update(self, user):
    if user.is_readonly:
        return False
    if user.is_admin:
        return True
    cprivs = ControllerSlicePrivilege.objects.filter(slice_privilege__user=user)
    for cpriv in dprivs:
        if cpriv.role.role == ['admin', 'Admin']:
            return True
    return False

@staticmethod
def select_by_user(user):
    if user.is_admin:
        qs = ControllerSlicePrivilege.objects.all()
    else:
        cpriv_ids = [cp.id for cp in ControllerSlicePrivilege.objects.filter(slice_privilege__user=user)]
        qs = ControllerSlicePrivilege.objects.filter(id__in=cpriv_ids)
    return qs
