from django.db import models
from core.models import PlCoreBase,SingletonModel,PlCoreBaseManager,User
from core.models.plcorebase import StrippedCharField
from xos.exceptions import *
from operator import attrgetter
import json

class Program(PlCoreBase):
    KIND_CHOICES = (('tosca', 'Tosca'), )
    COMMAND_CHOICES = (('run', 'Run'), ('destroy', 'Destroy'), )

    name = StrippedCharField(max_length=30, help_text="Service Name")
    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of Service")
    kind = StrippedCharField(max_length=30, help_text="Kind of service", choices=KIND_CHOICES)
    command = StrippedCharField(blank=True, null=True, max_length=30, help_text="Command to run", choices=COMMAND_CHOICES)

    owner = models.ForeignKey(User, null=True, related_name="programs")

    contents = models.TextField(blank=True, null=True, help_text="Contents of Program")
    output = models.TextField(blank=True, null=True, help_text="Output of Program")
    messages = models.TextField(blank=True, null=True, help_text="Debug messages")
    status = models.TextField(blank=True, null=True, max_length=30, help_text="Status of program")

    @classmethod
    def select_by_user(cls, user):
        return cls.objects.all()

    def __unicode__(self): return u'%s' % (self.name)

    def can_update(self, user):
        return True

    def save(self, *args, **kwargs):
        # set creator on first save
        if not self.owner and hasattr(self, 'caller'):
            self.owner = self.caller

        if (self.command in ["run", "destroy"]) and (self.status in ["complete", "exception"]):
            self.status = "queued"

        super(Program, self).save(*args, **kwargs)

