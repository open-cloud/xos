# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CeilometerService',
            fields=[
            ],
            options={
                'verbose_name': 'Ceilometer Service',
                'proxy': True,
            },
            bases=('core.service',),
        ),
        migrations.CreateModel(
            name='MonitoringChannel',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.tenantwithcontainer',),
        ),
        migrations.CreateModel(
            name='SFlowService',
            fields=[
            ],
            options={
                'verbose_name': 'sFlow Collection Service',
                'proxy': True,
            },
            bases=('core.service',),
        ),
        migrations.CreateModel(
            name='SFlowTenant',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.tenant',),
        ),
    ]
