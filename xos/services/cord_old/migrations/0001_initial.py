# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models.plcorebase
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessAgent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('enacted', models.DateTimeField(default=None, null=True, blank=True)),
                ('policed', models.DateTimeField(default=None, null=True, blank=True)),
                ('backend_register', models.CharField(default=b'{}', max_length=1024, null=True)),
                ('backend_status', models.CharField(default=b'0 - Provisioning in progress', max_length=1024)),
                ('deleted', models.BooleanField(default=False)),
                ('write_protect', models.BooleanField(default=False)),
                ('lazy_blocked', models.BooleanField(default=False)),
                ('no_sync', models.BooleanField(default=False)),
                ('no_policy', models.BooleanField(default=False)),
                ('name', models.CharField(help_text=b'name of agent', max_length=254)),
                ('mac', models.CharField(help_text=b'MAC Address or Access Agent', max_length=32, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model, core.models.plcorebase.PlModelMixIn),
        ),
        migrations.CreateModel(
            name='AccessDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('enacted', models.DateTimeField(default=None, null=True, blank=True)),
                ('policed', models.DateTimeField(default=None, null=True, blank=True)),
                ('backend_register', models.CharField(default=b'{}', max_length=1024, null=True)),
                ('backend_status', models.CharField(default=b'0 - Provisioning in progress', max_length=1024)),
                ('deleted', models.BooleanField(default=False)),
                ('write_protect', models.BooleanField(default=False)),
                ('lazy_blocked', models.BooleanField(default=False)),
                ('no_sync', models.BooleanField(default=False)),
                ('no_policy', models.BooleanField(default=False)),
                ('uplink', models.IntegerField(null=True, blank=True)),
                ('vlan', models.IntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model, core.models.plcorebase.PlModelMixIn),
        ),
        migrations.CreateModel(
            name='AgentPortMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('enacted', models.DateTimeField(default=None, null=True, blank=True)),
                ('policed', models.DateTimeField(default=None, null=True, blank=True)),
                ('backend_register', models.CharField(default=b'{}', max_length=1024, null=True)),
                ('backend_status', models.CharField(default=b'0 - Provisioning in progress', max_length=1024)),
                ('deleted', models.BooleanField(default=False)),
                ('write_protect', models.BooleanField(default=False)),
                ('lazy_blocked', models.BooleanField(default=False)),
                ('no_sync', models.BooleanField(default=False)),
                ('no_policy', models.BooleanField(default=False)),
                ('mac', models.CharField(help_text=b'MAC Address', max_length=32, null=True, blank=True)),
                ('port', models.CharField(help_text=b'Openflow port ID', max_length=32, null=True, blank=True)),
                ('access_agent', models.ForeignKey(related_name=b'port_mappings', to='cord.AccessAgent')),
            ],
            options={
            },
            bases=(models.Model, core.models.plcorebase.PlModelMixIn),
        ),
        migrations.CreateModel(
            name='VOLTDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('enacted', models.DateTimeField(default=None, null=True, blank=True)),
                ('policed', models.DateTimeField(default=None, null=True, blank=True)),
                ('backend_register', models.CharField(default=b'{}', max_length=1024, null=True)),
                ('backend_status', models.CharField(default=b'0 - Provisioning in progress', max_length=1024)),
                ('deleted', models.BooleanField(default=False)),
                ('write_protect', models.BooleanField(default=False)),
                ('lazy_blocked', models.BooleanField(default=False)),
                ('no_sync', models.BooleanField(default=False)),
                ('no_policy', models.BooleanField(default=False)),
                ('name', models.CharField(help_text=b'name of device', max_length=254)),
                ('openflow_id', models.CharField(help_text=b'OpenFlow ID', max_length=254, null=True, blank=True)),
                ('driver', models.CharField(help_text=b'driver', max_length=254, null=True, blank=True)),
                ('access_agent', models.ForeignKey(related_name=b'volt_devices', blank=True, to='cord.AccessAgent', null=True)),
            ],
            options={
            },
            bases=(models.Model, core.models.plcorebase.PlModelMixIn),
        ),
        migrations.CreateModel(
            name='VOLTService',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Service')),
            ],
            options={
                'verbose_name': 'vOLT Service',
            },
            bases=('core.service',),
        ),
        migrations.CreateModel(
            name='VOLTTenant',
            fields=[
                ('tenant_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Tenant')),
                ('s_tag', models.IntegerField(help_text=b's-tag', null=True, blank=True)),
                ('c_tag', models.IntegerField(help_text=b'c-tag', null=True, blank=True)),
                ('creator', models.ForeignKey(related_name=b'created_volts', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'vOLT Tenant',
            },
            bases=('core.tenant',),
        ),
        migrations.AddField(
            model_name='voltdevice',
            name='volt_service',
            field=models.ForeignKey(related_name=b'volt_devices', to='cord.VOLTService'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accessdevice',
            name='volt_device',
            field=models.ForeignKey(related_name=b'access_devices', to='cord.VOLTDevice'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accessagent',
            name='volt_service',
            field=models.ForeignKey(related_name=b'access_agents', to='cord.VOLTService'),
            preserve_default=True,
        ),
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
