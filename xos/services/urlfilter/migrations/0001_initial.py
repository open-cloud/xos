# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_network_ports'),
    ]

    operations = [
        migrations.CreateModel(
            name='UrlFilterService',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Service')),
            ],
            options={
                'verbose_name': 'URL Filter Service',
            },
            bases=('core.service', models.Model),
        ),
    ]
