# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import timezones.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_network_field_case'),
    ]

    operations = [
        migrations.RenameField(
            model_name='network',
            old_name='controllerParameters',
            new_name='controller_parameters',
        ),
        migrations.RenameField(
            model_name='network',
            old_name='controllerUrl',
            new_name='controller_url',
        ),
        migrations.RenameField(
            model_name='network',
            old_name='guaranteedBandwidth',
            new_name='guaranteed_bandwidth',
        ),
        migrations.RenameField(
            model_name='network',
            old_name='permitAllSlices',
            new_name='permit_all_slices',
        ),
        migrations.RenameField(
            model_name='network',
            old_name='permittedSlices',
            new_name='permitted_slices',
        ),
        migrations.RenameField(
            model_name='network',
            old_name='topologyParameters',
            new_name='topology_parameters',
        ),
    ]
