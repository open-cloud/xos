NETWORK_CHOICES = ((None, 'Default'), ('host', 'Host'), ('bridged', 'Bridged'), ('noauto', 'No Automatic Networks'))

@property
def slicename(self):
    return "%s_%s" % (self.site.login_base, self.name)

def save(self, *args, **kwds):
    site = Site.objects.get(id=self.site.id)
    # allow preexisting slices to keep their original name for now
    if not self.id and not self.name.startswith(site.login_base):
        raise XOSValidationError('slice name must begin with %s' % site.login_base, {'name' : 'slice name must begin with %s' % site.login_base})

    if self.name == site.login_base+"_":
        raise XOSValidationError('slice name is too short', {'name': 'slice name is too short'})

    if " " in self.name:
        raise XOSValidationError('slice name must not contain spaces', {'name': 'slice name must not contain spaces'})

    # set creator on first save
    if not self.creator and hasattr(self, 'caller'):
        self.creator = self.caller

    # only admins change a slice's creator
    if 'creator' in self.changed_fields and \
        (not hasattr(self, 'caller') or not self.caller.is_admin):

        if (self._initial["creator"]==None) and (self.creator==getattr(self,"caller",None)):
            # it's okay if the creator is being set by the caller to
            # himeself on a new slice object.
            pass
        else:
            raise PermissionDenied("Insufficient privileges to change slice creator",
                                   {'creator': "Insufficient privileges to change slice creator"})
    
    if not self.creator:
        raise XOSValidationError('slice has no creator', {'creator': 'slice has no creator'})

    if self.network=="Private Only":
        # "Private Only" was the default from the old Tenant View
        self.network=None
    self.enforce_choices(self.network, self.NETWORK_CHOICES)

    super(Slice, self).save(*args, **kwds)

def can_update(self, user):
    return user.can_update_slice(self)


@staticmethod
def select_by_user(user):
    if user.is_admin:
        qs = Slice.objects.all()
    else:
        from core.models.privilege import Privilege 
        # users can see slices they belong to 
        slice_ids = [sp.object_id for sp in Privilege.objects.filter(accessor_id=user.id, accessor_type='User', object_type='Slice')]
        # pis and admins can see slices at their sites
        site_ids = [sp.object_id for sp in Privilege.objects.filter(accessor_id=user.id, accessor_type='User', object_type='Site')\
                    if (sp.permission in ['role:pi', 'role:admin'])]
        sites = [Site.objects.get(pk = site_id) for site_id in site_ids]

        slice_ids.extend([s.id for s in Slice.objects.filter(site__in=sites)])
        qs = Slice.objects.filter(id__in=slice_ids)
    return qs


