# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kompomaatti', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgrammeEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField(help_text='Tapahtuman alkamisaika.', verbose_name='Alku')),
                ('end', models.DateTimeField(help_text='Tapahtuman loppumisaika.', null=True, verbose_name='Loppu', blank=True)),
                ('description', models.TextField(verbose_name='Kuvaus', blank=True)),
                ('title', models.CharField(help_text='Lyhyt otsikko.', max_length=128, verbose_name='Otsikko')),
                ('presenters', models.CharField(help_text='Esityksen pit\xe4j\xe4t tms.', max_length=256, verbose_name='Henkil\xf6t', blank=True)),
                ('presenters_titles', models.CharField(help_text='Henkil\xf6n arvo-, ammatti- tai virkanimike.', max_length=256, verbose_name='Nimikkeet', blank=True)),
                ('place', models.CharField(help_text='Tarkka paikka tapahtuma-areenalla', max_length=64, verbose_name='Paikka', blank=True)),
                ('icon_original', models.ImageField(help_text='Kuva 1 tapahtumalle.', upload_to=b'programme/images/', verbose_name='Kuva 1', blank=True)),
                ('icon2_original', models.ImageField(help_text='Kuva 2 tapahtumalle.', upload_to=b'programme/images/', verbose_name='Kuva 2', blank=True)),
                ('email', models.EmailField(help_text='Tapahtumaan liittyv\xe4 s\xe4hk\xf6posti-osoite (esim. esiintyj\xe4n).', max_length=75, verbose_name='S\xe4hk\xf6posti', blank=True)),
                ('home_url', models.URLField(help_text='Tapahtumaan liittyv\xe4 URL.', verbose_name='Kotiurli', blank=True)),
                ('twitter_url', models.URLField(help_text='Tapahtumaan liittyv\xe4 Twitter-url.', verbose_name='Twitter', blank=True)),
                ('github_url', models.URLField(help_text='Tapahtumaan liittyv\xe4 Github-url', verbose_name='Github', blank=True)),
                ('facebook_url', models.URLField(help_text='Tapahtumaan liittyv\xe4 facebook-url.', verbose_name='Facebook', blank=True)),
                ('linkedin_url', models.URLField(help_text='Tapahtumaan liittyv\xe4 LinkedIn-url.', verbose_name='LinkedIn', blank=True)),
                ('wiki_url', models.URLField(help_text='Tapahtumaan liittyv\xe4 Wikipedia-url.', verbose_name='Wikipedia', blank=True)),
                ('gplus_url', models.URLField(help_text='Tapahtumaan liittyv\xe4 Google Plus-url.', verbose_name='Google+', blank=True)),
                ('event_type', models.IntegerField(default=0, help_text='M\xe4\xe4ritt\xe4\xe4 tapahtuman tyypin. Yksityiskohtaiset tapahtumat n\xe4kyv\xe4t etusivun tapahtumalistassa.', verbose_name='Tapahtuman tyyppi', choices=[(0, 'Yksinkertainen'), (1, 'Yksityiskohtainen')])),
                ('active', models.BooleanField(default=True, help_text='Deaktivoidut piilotetaan.', verbose_name='Aktiivinen')),
                ('event', models.ForeignKey(verbose_name='Tapahtuma', to='kompomaatti.Event')),
            ],
            options={
                'verbose_name': 'ohjelmatapahtuma',
                'verbose_name_plural': 'ohjelmatapahtumat',
            },
            bases=(models.Model,),
        ),
    ]
