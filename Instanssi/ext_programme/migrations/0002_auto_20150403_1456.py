# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ext_programme', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programmeevent',
            name='email',
            field=models.EmailField(help_text='Tapahtumaan liittyv\xe4 s\xe4hk\xf6posti-osoite (esim. esiintyj\xe4n).', max_length=254, verbose_name='S\xe4hk\xf6posti', blank=True),
        ),
    ]
