# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20141111_2311'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ImageDeployments',
        ),
        migrations.DeleteModel(
            name='SiteDeployments',
        ),
        migrations.DeleteModel(
            name='SliceDeployments',
        ),
        migrations.DeleteModel(
            name='UserDeployments',
        ),
    ]
