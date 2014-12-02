# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('kompomaatti', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DBLogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('module', models.CharField(max_length=64, blank=True)),
                ('level', models.CharField(max_length=10)),
                ('message', models.TextField()),
                ('event', models.ForeignKey(blank=True, to='kompomaatti.Event', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'lokimerkint\xe4',
                'verbose_name_plural': 'lokimerkinn\xe4t',
            },
            bases=(models.Model,),
        ),
    ]
