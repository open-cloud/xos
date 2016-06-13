# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CordSubscriberRoot',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.subscriber',),
        ),
        migrations.CreateModel(
            name='VBNGService',
            fields=[
            ],
            options={
                'verbose_name': 'vBNG Service',
                'proxy': True,
            },
            bases=('core.service',),
        ),
        migrations.CreateModel(
            name='VBNGTenant',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.tenant',),
        ),
        migrations.CreateModel(
            name='VOLTService',
            fields=[
            ],
            options={
                'verbose_name': 'vOLT Service',
                'proxy': True,
            },
            bases=('core.service',),
        ),
        migrations.CreateModel(
            name='VOLTTenant',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.tenant',),
        ),
        migrations.CreateModel(
            name='VSGService',
            fields=[
            ],
            options={
                'verbose_name': 'vSG Service',
                'proxy': True,
            },
            bases=('core.service',),
        ),
        migrations.CreateModel(
            name='VSGTenant',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.tenantwithcontainer',),
        ),
    ]
