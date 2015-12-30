# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestRouterService',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Service')),
                ('behindNat', models.BooleanField(default=False, help_text=b"Enables 'Behind NAT' mode.")),
                ('defaultTTL', models.PositiveIntegerField(default=30, help_text=b'DNS response time-to-live(TTL)')),
                ('defaultAction', models.CharField(default=b'best', help_text=b'Review if this should be enum', max_length=30)),
                ('lastResortAction', models.CharField(default=b'random', help_text=b'Review if this should be enum', max_length=30)),
                ('maxAnswers', models.PositiveIntegerField(default=3, help_text=b'Maximum number of answers in DNS response.')),
            ],
            options={
                'verbose_name': 'Request Router Service',
            },
            bases=('core.service', models.Model),
        ),
        migrations.CreateModel(
            name='ServiceMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('enacted', models.DateTimeField(default=None, null=True, blank=True)),
                ('backend_status', models.CharField(default=b'Provisioning in progress', max_length=140)),
                ('deleted', models.BooleanField(default=False)),
                ('name', models.SlugField(help_text=b'name of this service map', unique=True)),
                ('prefix', models.CharField(help_text=b'FQDN of the region of URI space managed by RR on behalf of this service', max_length=256)),
                ('siteMap', models.FileField(help_text=b'maps client requests to service instances', upload_to=b'maps/', blank=True)),
                ('accessMap', models.FileField(help_text=b'specifies which client requests are allowed', upload_to=b'maps/', blank=True)),
                ('owner', models.ForeignKey(help_text=b'service which owns this map', to='core.Service')),
                ('slice', models.ForeignKey(help_text=b'slice that implements this service', to='core.Slice')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
