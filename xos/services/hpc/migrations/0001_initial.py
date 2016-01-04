# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(
                    help_text=b'Name of the Access Map', max_length=64)),
                ('description', models.TextField(
                    max_length=130, null=True, blank=True)),
                ('map', models.FileField(
                    help_text=b'specifies which client requests are allowed', upload_to=b'maps/')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CDNPrefix',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(
                    default=django.utils.timezone.now, auto_now_add=True)),
                ('updated', models.DateTimeField(
                    default=django.utils.timezone.now, auto_now=True)),
                ('enacted', models.DateTimeField(
                    default=None, null=True, blank=True)),
                ('backend_status', models.CharField(
                    default=b'Provisioning in progress', max_length=140)),
                ('deleted', models.BooleanField(default=False)),
                ('cdn_prefix_id', models.IntegerField(null=True, blank=True)),
                ('prefix', models.CharField(
                    help_text=b'Registered Prefix for Domain', max_length=200)),
                ('description', models.TextField(
                    help_text=b'Description of Content Provider', max_length=254, null=True, blank=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContentProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(
                    default=django.utils.timezone.now, auto_now_add=True)),
                ('updated', models.DateTimeField(
                    default=django.utils.timezone.now, auto_now=True)),
                ('enacted', models.DateTimeField(
                    default=None, null=True, blank=True)),
                ('backend_status', models.CharField(
                    default=b'Provisioning in progress', max_length=140)),
                ('deleted', models.BooleanField(default=False)),
                ('content_provider_id', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=254)),
                ('enabled', models.BooleanField(default=True)),
                ('description', models.TextField(
                    help_text=b'Description of Content Provider', max_length=254, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HpcService',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True,
                                                     primary_key=True, serialize=False, to='core.Service')),
            ],
            options={
                'verbose_name': 'HPC Service',
            },
            bases=('core.service', models.Model),
        ),
        migrations.CreateModel(
            name='OriginServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(
                    default=django.utils.timezone.now, auto_now_add=True)),
                ('updated', models.DateTimeField(
                    default=django.utils.timezone.now, auto_now=True)),
                ('enacted', models.DateTimeField(
                    default=None, null=True, blank=True)),
                ('backend_status', models.CharField(
                    default=b'Provisioning in progress', max_length=140)),
                ('deleted', models.BooleanField(default=False)),
                ('origin_server_id', models.IntegerField(null=True, blank=True)),
                ('url', models.URLField()),
                ('authenticated', models.BooleanField(
                    default=False, help_text=b'Status for this Site')),
                ('enabled', models.BooleanField(
                    default=True, help_text=b'Status for this Site')),
                ('protocol', models.CharField(default=b'HTTP', max_length=12, choices=[
                 (b'http', b'HTTP'), (b'rtmp', b'RTMP'), (b'rtp', b'RTP'), (b'shout', b'SHOUTcast')])),
                ('redirects', models.BooleanField(
                    default=True, help_text=b'Indicates whether Origin Server redirects should be used for this Origin Server')),
                ('description', models.TextField(
                    max_length=255, null=True, blank=True)),
                ('contentProvider', models.ForeignKey(to='hpc.ContentProvider')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(
                    default=django.utils.timezone.now, auto_now_add=True)),
                ('updated', models.DateTimeField(
                    default=django.utils.timezone.now, auto_now=True)),
                ('enacted', models.DateTimeField(
                    default=None, null=True, blank=True)),
                ('backend_status', models.CharField(
                    default=b'Provisioning in progress', max_length=140)),
                ('deleted', models.BooleanField(default=False)),
                ('service_provider_id', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(
                    help_text=b'Service Provider Name', max_length=254)),
                ('description', models.TextField(
                    help_text=b'Description of Service Provider', max_length=254, null=True, blank=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SiteMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(
                    help_text=b'Name of the Site Map', max_length=64)),
                ('description', models.TextField(
                    max_length=130, null=True, blank=True)),
                ('map', models.FileField(
                    help_text=b'specifies how to map requests to hpc instances', upload_to=b'maps/')),
                ('contentProvider', models.ForeignKey(
                    blank=True, to='hpc.ContentProvider', null=True)),
                ('serviceProvider', models.ForeignKey(
                    blank=True, to='hpc.ServiceProvider', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='contentprovider',
            name='serviceProvider',
            field=models.ForeignKey(to='hpc.ServiceProvider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contentprovider',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cdnprefix',
            name='contentProvider',
            field=models.ForeignKey(to='hpc.ContentProvider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cdnprefix',
            name='defaultOriginServer',
            field=models.ForeignKey(
                blank=True, to='hpc.OriginServer', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accessmap',
            name='contentProvider',
            field=models.ForeignKey(to='hpc.ContentProvider'),
            preserve_default=True,
        ),
    ]
