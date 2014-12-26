# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CassandraService',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Service')),
                ('clusterSize', models.PositiveIntegerField(default=1)),
                ('replicationFactor', models.PositiveIntegerField(default=1)),
            ],
            options={
                'verbose_name': 'Cassandra Service',
            },
            bases=('core.service', models.Model),
        ),
    ]
