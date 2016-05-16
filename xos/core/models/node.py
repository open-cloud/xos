import os
from django.db import models
from core.models import PlCoreBase
from core.models.plcorebase import StrippedCharField
from core.models.site import Site, SiteDeployment, SitePrivilege
from core.models import Tag
from django.contrib.contenttypes import generic

# Create your models here.

class Node(PlCoreBase):
    name = StrippedCharField(max_length=200, unique=True, help_text="Name of the Node")
    site_deployment = models.ForeignKey(SiteDeployment, related_name='nodes')
    site = models.ForeignKey(Site, null=True, blank=True, related_name='nodes')
    tags = generic.GenericRelation(Tag)

    def __unicode__(self):  return u'%s' % (self.name)

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.no_sync=True

    def save(self, *args, **kwds):
        if self.site is None and self.site_deployment is not None:
            self.site = self.site_deployment.site

        super(Node, self).save(*args, **kwds)

    def can_update(self, user):
        return user.can_update_site(self.site, allow=['tech'])

class NodeLabel(PlCoreBase):
    name = StrippedCharField(max_length=200, help_text="label name", unique=True)
    node = models.ManyToManyField(Node, related_name="nodelabels", blank=True)

    def __unicode__(self): return u'%s' % (self.name)
