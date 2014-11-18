# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models.network
import timezones.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20141006_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='network',
            name='ports',
            field=models.CharField(blank=True, max_length=1024, null=True, validators=[core.models.network.ValidateNatList]),
        ),
    ]
