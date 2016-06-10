# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MCORDService',
            fields=[
            ],
            options={
                'verbose_name': 'MCORD Service',
                'proxy': True,
            },
            bases=('core.service',),
        ),
        migrations.CreateModel(
            name='VBBUComponent',
            fields=[
            ],
            options={
                'verbose_name': 'VBBU MCORD Service Component',
                'proxy': True,
            },
            bases=('core.tenantwithcontainer',),
        ),
        migrations.CreateModel(
            name='VPGWCComponent',
            fields=[
            ],
            options={
                'verbose_name': 'VPGWC MCORD Service Component',
                'proxy': True,
            },
            bases=('core.tenantwithcontainer',),
        ),
    ]
