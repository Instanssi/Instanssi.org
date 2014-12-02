# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kompomaatti', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtherVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Videon nimi.', max_length=64, verbose_name='Nimi')),
                ('description', models.TextField(help_text='Videon kuvaus.', verbose_name='Kuvaus')),
                ('youtube_url', models.URLField(help_text='Linkki teoksen Youtube-versioon.', verbose_name='Youtube URL', blank=True)),
            ],
            options={
                'verbose_name': 'muu video',
                'verbose_name_plural': 'muut videot',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OtherVideoCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Kategorian nimi', max_length=64, verbose_name='Nimi')),
                ('event', models.ForeignKey(verbose_name='Tapahtuma', to='kompomaatti.Event')),
            ],
            options={
                'verbose_name': 'videokategoria',
                'verbose_name_plural': 'videokategoriat',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='othervideo',
            name='category',
            field=models.ForeignKey(verbose_name='Kategoria', to='arkisto.OtherVideoCategory'),
            preserve_default=True,
        ),
    ]
