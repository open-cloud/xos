class Meta:
    unique_together = ('controller', 'site_privilege', 'role_id')

def can_update(self, user):
    if user.is_readonly:
        return False
    if user.is_admin:
        return True
    cprivs = ControllerSitePrivilege.objects.filter(site_privilege__user=user)
    for cpriv in dprivs:
        if cpriv.site_privilege.role.role == ['admin', 'Admin']:
            return True
    return False

@staticmethod
def select_by_user(user):
    if user.is_admin:
        qs = ControllerSitePrivilege.objects.all()
    else:
        cpriv_ids = [cp.id for cp in ControllerSitePrivilege.objects.filter(site_privilege__user=user)]
        qs = ControllerSitePrivilege.objects.filter(id__in=cpriv_ids)
    return qs
