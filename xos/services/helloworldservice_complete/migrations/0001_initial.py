# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelloWorldServiceComplete',
            fields=[
            ],
            options={
                'verbose_name': 'Hello World Service',
                'proxy': True,
            },
            bases=('core.service',),
        ),
        migrations.CreateModel(
            name='HelloWorldTenantComplete',
            fields=[
            ],
            options={
                'verbose_name': 'Hello World Tenant',
                'proxy': True,
            },
            bases=('core.tenantwithcontainer',),
        ),
    ]
