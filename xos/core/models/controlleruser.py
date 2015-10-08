import os
import datetime
from collections import defaultdict
from django.db import models
from django.db.models import F, Q
from core.models import PlCoreBase,User,Controller
from core.models.plcorebase import StrippedCharField
from core.models import Controller,ControllerLinkManager,ControllerLinkDeletionManager

class ControllerUser(PlCoreBase):
    objects = ControllerLinkManager()
    deleted_objects = ControllerLinkDeletionManager()

    user = models.ForeignKey(User,related_name='controllerusers')
    controller = models.ForeignKey(Controller,related_name='controllersusers')
    kuser_id = StrippedCharField(null=True, blank=True, max_length=200, help_text="Keystone user id")


    class Meta:
        unique_together = ('user', 'controller')

    def __unicode__(self):  return u'%s %s' % (self.controller, self.user)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = ControllerUser.objects.all()
        else:
            users = User.select_by_user(user)
            qs = ControllerUser.objects.filter(user__in=users)
        return qs

    def can_update(self, user):
        return user.can_update_root()    


class ControllerSitePrivilege(PlCoreBase):
    objects = ControllerLinkManager()
    deleted_objects = ControllerLinkDeletionManager()

    controller = models.ForeignKey('Controller', related_name='controllersiteprivileges')
    site_privilege = models.ForeignKey('SitePrivilege', related_name='controllersiteprivileges')
    role_id = StrippedCharField(null=True, blank=True, max_length=200, db_index=True, help_text="Keystone id")

    class Meta:
        unique_together = ('controller', 'site_privilege', 'role_id')

    def __unicode__(self):  return u'%s %s' % (self.controller, self.site_privilege)

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


class ControllerSlicePrivilege(PlCoreBase):
    objects = ControllerLinkManager()
    deleted_objects = ControllerLinkDeletionManager()

    controller = models.ForeignKey('Controller', related_name='controllersliceprivileges')
    slice_privilege = models.ForeignKey('SlicePrivilege', related_name='controllersliceprivileges')
    role_id = StrippedCharField(null=True, blank=True, max_length=200, db_index=True, help_text="Keystone id")


    class Meta:
        unique_together = ('controller', 'slice_privilege')

    def __unicode__(self):  return u'%s %s' % (self.controller, self.slice_privilege)

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

