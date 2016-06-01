import os
from django.db import models
from core.models import PlCoreBase
from core.models.plcorebase import StrippedCharField

# XOS: Serves as the root of the build system

class XOS(PlCoreBase):
    name = StrippedCharField(max_length=200, unique=True, help_text="Name of XOS", default="XOS")

    def __unicode__(self):  return u'%s' % (self.name)

    def __init__(self, *args, **kwargs):
        super(XOS, self).__init__(*args, **kwargs)

    def save(self, *args, **kwds):
        super(XOS, self).save(*args, **kwds)

#    def can_update(self, user):
#        return user.can_update_site(self.site, allow=['tech'])

    def rebuild(self):
        for service_controller in self.service_controllers.all():
            for scr in service_controller.service_controller_resources.all():
               scr.save()
            service_controller.save()
        self.save()


