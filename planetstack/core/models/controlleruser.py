import os
import datetime
from collections import defaultdict
from django.db import models
from django.db.models import F, Q
from core.models import PlCoreBase,User,Controller
from core.models import Controller,ControllerLinkManager,ControllerLinkDeletionManager

class ControllerUsers(PlCoreBase):
    objects = ControllerLinkManager()
    deleted_objects = ControllerLinkDeletionManager()

    user = models.ForeignKey(User,related_name='controllerusers')
    controller = models.ForeignKey(Controller,related_name='controllersusers')
    kuser_id = models.CharField(null=True, blank=True, max_length=200, help_text="Keystone user id")

    def __unicode__(self):  return u'%s %s' % (self.controller, self.user)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = ControllerUsers.objects.all()
        else:
            users = Users.select_by_user(user)
            qs = ControllerUsers.objects.filter(user__in=users)
        return qs
