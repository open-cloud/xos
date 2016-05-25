# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ONOSApp',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.tenant',),
        ),
        migrations.CreateModel(
            name='ONOSService',
            fields=[
            ],
            options={
                'verbose_name': 'ONOS Service',
                'proxy': True,
            },
            bases=('core.service',),
        ),
    ]
