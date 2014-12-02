# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ToimistoJahti',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text='Avain', unique=True, max_length=10, verbose_name='Avain')),
                ('help', models.TextField(help_text='Ohjeteksti', verbose_name='Ohje')),
            ],
            options={
                'verbose_name': 'jahtitehtava',
                'verbose_name_plural': 'jahtitehtavat',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ToimistoSuoritus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nick', models.CharField(help_text='Agentin tunnusnimi', unique=True, max_length=32, verbose_name='Tunnusnimi')),
                ('time', models.DateTimeField(help_text='Aika, jolloin agentti merkkasi teht\xe4v\xe4n suoritetuksi', verbose_name='Suoritusaika')),
                ('user', models.ForeignKey(verbose_name='K\xe4ytt\xe4j\xe4', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'toimistosuoritus',
                'verbose_name_plural': 'toimistosuoritukset',
            },
            bases=(models.Model,),
        ),
    ]
