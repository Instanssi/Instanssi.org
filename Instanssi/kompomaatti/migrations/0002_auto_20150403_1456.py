# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('kompomaatti', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votecoderequest',
            name='user',
            field=models.OneToOneField(verbose_name='K\xe4ytt\xe4j\xe4', to=settings.AUTH_USER_MODEL, help_text='Pyynn\xf6n esitt\xe4nyt k\xe4ytt\xe4j\xe4'),
        ),
    ]
