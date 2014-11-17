# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20141107_0245'),
    ]

    operations = [
        migrations.CreateModel(
            name='Composition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('enacted', models.DateTimeField(default=None, null=True)),
                ('backend_status', models.CharField(default=b'Provisioning in progress', max_length=140)),
                ('deleted', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompositionService',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Service')),
            ],
            options={
                'verbose_name': 'Service Composition Service',
            },
            bases=('core.service', models.Model),
        ),
        migrations.CreateModel(
            name='CompositionServiceThrough',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('enacted', models.DateTimeField(default=None, null=True)),
                ('backend_status', models.CharField(default=b'Provisioning in progress', max_length=140)),
                ('deleted', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('composition', models.ForeignKey(to='servcomp.Composition')),
                ('service', models.ForeignKey(related_name=b'compositions', to='core.Service')),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EndUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('enacted', models.DateTimeField(default=None, null=True)),
                ('backend_status', models.CharField(default=b'Provisioning in progress', max_length=140)),
                ('deleted', models.BooleanField(default=False)),
                ('email', models.CharField(max_length=255)),
                ('firstName', models.CharField(max_length=80)),
                ('lastName', models.CharField(max_length=80)),
                ('macAddress', models.CharField(max_length=80)),
                ('composition', models.ForeignKey(related_name=b'endUsers', blank=True, to='servcomp.Composition', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='composition',
            name='services',
            field=models.ManyToManyField(to='core.Service', through='servcomp.CompositionServiceThrough', blank=True),
            preserve_default=True,
        ),
    ]
