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
    extra_hosts = StrippedCharField(max_length=1024, help_text="list of hostname mappings that will be passed to docker-compose", null=True, blank=True)
    no_start = models.BooleanField(help_text="Do not start the XOS UI inside of the UI docker container", default=False)

    def __unicode__(self):  return u'%s' % (self.name)

    def __init__(self, *args, **kwargs):
        super(XOS, self).__init__(*args, **kwargs)

    def save(self, *args, **kwds):
        super(XOS, self).save(*args, **kwds)

#    def can_update(self, user):
#        return user.can_update_site(self.site, allow=['tech'])

    def rebuild(self, services=[]):
        # If `services` is empty, then only rebuild the UI
        # Otherwise, only rebuild the services listed in `services`
        with transaction.atomic():
            for loadable_module in self.loadable_modules.all():
                if (services) and (loadable_module.name not in services):
                    continue
                for lmr in loadable_module.loadable_module_resources.all():
                   lmr.save()
                loadable_module.save()
            self.save()

class XOSVolume(PlCoreBase):
    xos = models.ForeignKey(XOS, related_name='volumes', help_text="The XOS object for this Volume")
    container_path=StrippedCharField(max_length=1024, unique=True, help_text="Path of Volume in Container")
    host_path=StrippedCharField(max_length=1024, help_text="Path of Volume in Host")
    read_only=models.BooleanField(default=False, help_text="True if mount read-only")

    def __unicode__(self): return u'%s' % (self.container_path)


