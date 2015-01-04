# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import timezones.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_network_field_case'),
    ]

    operations = [
        migrations.RenameField(
            model_name='slice',
            old_name='imagePreference',
            new_name='image_preference',
        ),
        migrations.RenameField(
            model_name='slice',
            old_name='mountDataSets',
            new_name='mount_data_sets',
        ),
    ]
