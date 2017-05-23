def save(self, *args, **kwds):
    if not self.user.is_active:
        raise PermissionDenied, "Cannot modify role(s) of a disabled user"
    super(TenantPrivilege, self).save(*args, **kwds)

def can_update(self, user):
    return user.can_update_tenant_privilege(self)

@classmethod
def select_by_user(cls, user):
    if user.is_admin:
        return cls.objects.all()
    else:
        # User can see his own privilege
        trp_ids = [trp.id for trp in cls.objects.filter(user=user)]

        # A tenant admin can see the TenantPrivileges for their Tenants
        for priv in cls.objects.filter(user=user, role__role="admin"):
            trp_ids.extend(
                [trp.id for trp in cls.objects.filter(tenant=priv.tenant)])

        return cls.objects.filter(id__in=trp_ids)
