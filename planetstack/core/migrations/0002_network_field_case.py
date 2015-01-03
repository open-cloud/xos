# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import timezones.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='networktemplate',
            old_name='controllerKind',
            new_name='controller_kind',
        ),
        migrations.RenameField(
            model_name='networktemplate',
            old_name='guaranteedBandwidth',
            new_name='guaranteed_bandwidth',
        ),
        migrations.RenameField(
            model_name='networktemplate',
            old_name='sharedNetworkId',
            new_name='shared_network_id',
        ),
        migrations.RenameField(
            model_name='networktemplate',
            old_name='sharedNetworkName',
            new_name='shared_network_name',
        ),
        migrations.RenameField(
            model_name='networktemplate',
            old_name='topologyKind',
            new_name='topology_kind',
        ),
    ]
