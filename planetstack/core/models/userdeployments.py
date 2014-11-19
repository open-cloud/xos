import os
import datetime
from collections import defaultdict
from django.db import models
from django.db.models import F, Q
from core.models import PlCoreBase,Site,User,Deployment
from core.models import Deployment,DeploymentLinkManager,DeploymentLinkDeletionManager

class UserDeployments(PlCoreBase):
    objects = DeploymentLinkManager()
    deleted_objects = DeploymentLinkDeletionManager()

    user = models.ForeignKey(User,related_name='userdeployments')
    deployment = models.ForeignKey(Deployment,related_name='userdeployments')
    kuser_id = models.CharField(null=True, blank=True, max_length=200, help_text="Keystone user id")

    def __unicode__(self):  return u'%s %s' % (self.user, self.deployment.name)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = UserDeployments.objects.all()
        else:
            users = Users.select_by_user(user)
            qs = Usereployments.objects.filter(user__in=slices)
        return qs
