# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20150118_1926'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='instance_uuid',
            field=models.CharField(help_text=b'Nova instance uuid', max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
    ]
