# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_omf_friendly_default_false'),
    ]

    operations = [
        migrations.CreateModel(
            name='KairosDBService',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Service')),
            ],
            options={
                'verbose_name': 'KairosDB Service',
            },
            bases=('core.service', models.Model),
        ),
    ]
