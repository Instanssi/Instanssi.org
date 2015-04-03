# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('screenshow', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screenconfig',
            name='event',
            field=models.OneToOneField(verbose_name='Tapahtuma', to='kompomaatti.Event'),
        ),
    ]
