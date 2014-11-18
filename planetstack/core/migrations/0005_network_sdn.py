# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20141006_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='network',
            name='controllerParameters',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='network',
            name='topologyParameters',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='networktemplate',
            name='controllerKind',
            field=models.CharField(default=None, max_length=30, null=True, blank=True, choices=[(None, b'None'), (b'onos', b'ONOS'), (b'custom', b'Custom')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='networktemplate',
            name='topologyKind',
            field=models.CharField(default=b'BigSwitch', max_length=30, choices=[(b'bigswitch', b'BigSwitch'), (b'physical', b'Physical'), (b'custom', b'Custom')]),
            preserve_default=True,
        ),
    ]
