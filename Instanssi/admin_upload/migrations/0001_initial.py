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
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(help_text='Lyhyt kuvaus siit\xe4, mihin/miss\xe4 tiedostoa k\xe4ytet\xe4\xe4n.', verbose_name='Kuvaus', blank=True)),
                ('file', models.FileField(upload_to=b'files/', verbose_name='Tiedosto')),
                ('date', models.DateTimeField(verbose_name='Aika')),
                ('event', models.ForeignKey(verbose_name='Tapahtuma', to='kompomaatti.Event')),
                ('user', models.ForeignKey(verbose_name='K\xe4ytt\xe4j\xe4', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'tiedosto',
                'verbose_name_plural': 'tiedostot',
            },
            bases=(models.Model,),
        ),
    ]
