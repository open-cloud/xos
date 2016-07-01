import os
from django.db import models, transaction
from core.models import PlCoreBase
from core.models.plcorebase import StrippedCharField

# XOS: Serves as the root of the build system



class XOS(PlCoreBase):
    name = StrippedCharField(max_length=200, unique=True, help_text="Name of XOS", default="XOS")
    ui_port = models.IntegerField(help_text="Port for XOS UI", default=80)
    bootstrap_ui_port = models.IntegerField(help_text="Port for XOS UI", default=81)
    db_container_name = StrippedCharField(max_length=200, help_text="name of XOS db container", default="xos_db")
    docker_project_name = StrippedCharField(max_length=200, help_text="docker project name")
    db_container_name = StrippedCharField(max_length=200, help_text="database container name")
    enable_build = models.BooleanField(help_text="True if Onboarding Synchronizer should build XOS as necessary", default=True)
    frontend_only = models.BooleanField(help_text="If True, XOS will not start synchronizer containers", default=False)
    source_ui_image = StrippedCharField(max_length=200, default="xosproject/xos")

    def __unicode__(self):  return u'%s' % (self.name)

    def __init__(self, *args, **kwargs):
        super(XOS, self).__init__(*args, **kwargs)

    def save(self, *args, **kwds):
        super(XOS, self).save(*args, **kwds)

#    def can_update(self, user):
#        return user.can_update_site(self.site, allow=['tech'])

    def rebuild(self):
        with transaction.atomic():
            for service_controller in self.service_controllers.all():
                for scr in service_controller.service_controller_resources.all():
                   scr.save()
                service_controller.save()
            self.save()

class XOSVolume(PlCoreBase):
    xos = models.ForeignKey(XOS, related_name='volumes', help_text="The XOS object for this Volume")
    container_path=StrippedCharField(max_length=1024, unique=True, help_text="Path of Volume in Container")
    host_path=StrippedCharField(max_length=1024, help_text="Path of Volume in Host")
    read_only=models.BooleanField(default=False, help_text="True if mount read-only")

    def __unicode__(self): return u'%s' % (self.container_path)


