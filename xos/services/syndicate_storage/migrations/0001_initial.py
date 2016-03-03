# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models.plcorebase
from django.conf import settings
import django.utils.timezone
import services.syndicate_storage.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SliceSecret',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('secret', services.syndicate_storage.models.ObserverSecretValue(help_text=b"Shared secret between OpenCloud and this slice's Syndicate daemons.", blank=True)),
                ('slice_id', models.ForeignKey(to='core.Slice')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SyndicatePrincipal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('enacted', models.DateTimeField(default=None, null=True, blank=True)),
                ('policed', models.DateTimeField(default=None, null=True, blank=True)),
                ('backend_register', models.CharField(default=b'{}', max_length=140, null=True)),
                ('backend_status', models.CharField(default=b'0 - Provisioning in progress', max_length=1024)),
                ('deleted', models.BooleanField(default=False)),
                ('write_protect', models.BooleanField(default=False)),
                ('lazy_blocked', models.BooleanField(default=False)),
                ('no_sync', models.BooleanField(default=False)),
                ('principal_id', models.TextField(unique=True)),
                ('public_key_pem', models.TextField()),
                ('sealed_private_key', models.TextField()),
            ],
            options={
            },
            bases=(models.Model, core.models.plcorebase.PlModelMixIn),
        ),
        migrations.CreateModel(
            name='SyndicateService',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Service')),
            ],
            options={
                'verbose_name': 'Syndicate Service',
                'verbose_name_plural': 'Syndicate Service',
            },
            bases=('core.service', models.Model),
        ),
        migrations.CreateModel(
            name='Volume',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('enacted', models.DateTimeField(default=None, null=True, blank=True)),
                ('policed', models.DateTimeField(default=None, null=True, blank=True)),
                ('backend_register', models.CharField(default=b'{}', max_length=140, null=True)),
                ('backend_status', models.CharField(default=b'0 - Provisioning in progress', max_length=1024)),
                ('deleted', models.BooleanField(default=False)),
                ('write_protect', models.BooleanField(default=False)),
                ('lazy_blocked', models.BooleanField(default=False)),
                ('no_sync', models.BooleanField(default=False)),
                ('name', models.CharField(help_text=b'Human-readable, searchable name of the Volume', max_length=64)),
                ('description', models.TextField(help_text=b'Human-readable description of what this Volume is used for.', max_length=130, null=True, blank=True)),
                ('blocksize', models.PositiveIntegerField(help_text=b'Number of bytes per block.')),
                ('private', models.BooleanField(default=True, help_text=b'Indicates if the Volume is visible to users other than the Volume Owner and Syndicate Administrators.')),
                ('archive', models.BooleanField(default=False, help_text=b'Indicates if this Volume is read-only, and only an Aquisition Gateway owned by the Volume owner (or Syndicate admin) can write to it.')),
                ('cap_read_data', models.BooleanField(default=True, help_text=b'VM can read Volume data')),
                ('cap_write_data', models.BooleanField(default=True, help_text=b'VM can write Volume data')),
                ('cap_host_data', models.BooleanField(default=True, help_text=b'VM can host Volume data')),
                ('owner_id', models.ForeignKey(verbose_name=b'Owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model, core.models.plcorebase.PlModelMixIn),
        ),
        migrations.CreateModel(
            name='VolumeAccessRight',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('enacted', models.DateTimeField(default=None, null=True, blank=True)),
                ('policed', models.DateTimeField(default=None, null=True, blank=True)),
                ('backend_register', models.CharField(default=b'{}', max_length=140, null=True)),
                ('backend_status', models.CharField(default=b'0 - Provisioning in progress', max_length=1024)),
                ('deleted', models.BooleanField(default=False)),
                ('write_protect', models.BooleanField(default=False)),
                ('lazy_blocked', models.BooleanField(default=False)),
                ('no_sync', models.BooleanField(default=False)),
                ('cap_read_data', models.BooleanField(default=True, help_text=b'VM can read Volume data')),
                ('cap_write_data', models.BooleanField(default=True, help_text=b'VM can write Volume data')),
                ('cap_host_data', models.BooleanField(default=True, help_text=b'VM can host Volume data')),
                ('owner_id', models.ForeignKey(verbose_name=b'user', to=settings.AUTH_USER_MODEL)),
                ('volume', models.ForeignKey(to='syndicate_storage.Volume')),
            ],
            options={
            },
            bases=(models.Model, core.models.plcorebase.PlModelMixIn),
        ),
        migrations.CreateModel(
            name='VolumeSlice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('enacted', models.DateTimeField(default=None, null=True, blank=True)),
                ('policed', models.DateTimeField(default=None, null=True, blank=True)),
                ('backend_register', models.CharField(default=b'{}', max_length=140, null=True)),
                ('backend_status', models.CharField(default=b'0 - Provisioning in progress', max_length=1024)),
                ('deleted', models.BooleanField(default=False)),
                ('write_protect', models.BooleanField(default=False)),
                ('lazy_blocked', models.BooleanField(default=False)),
                ('no_sync', models.BooleanField(default=False)),
                ('cap_read_data', models.BooleanField(default=True, help_text=b'VM can read Volume data')),
                ('cap_write_data', models.BooleanField(default=True, help_text=b'VM can write Volume data')),
                ('cap_host_data', models.BooleanField(default=True, help_text=b'VM can host Volume data')),
                ('UG_portnum', models.PositiveIntegerField(help_text=b'User Gateway port.  Any port above 1024 will work, but it must be available slice-wide.', verbose_name=b'UG port')),
                ('RG_portnum', models.PositiveIntegerField(help_text=b'Replica Gateway port.  Any port above 1024 will work, but it must be available slice-wide.', verbose_name=b'RG port')),
                ('credentials_blob', models.TextField(help_text=b'Encrypted slice credentials, sealed with the slice secret.', null=True, blank=True)),
                ('slice_id', models.ForeignKey(verbose_name=b'Slice', to='core.Slice')),
                ('volume_id', models.ForeignKey(verbose_name=b'Volume', to='syndicate_storage.Volume')),
            ],
            options={
            },
            bases=(models.Model, core.models.plcorebase.PlModelMixIn),
        ),
        migrations.AddField(
            model_name='volume',
            name='slice_id',
            field=models.ManyToManyField(to='core.Slice', through='syndicate_storage.VolumeSlice'),
            preserve_default=True,
        ),
    ]
