# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-11 17:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('kompomaatti', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IRCMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='Aika')),
                ('nick', models.CharField(max_length=64, verbose_name='Nimimerkki')),
                ('message', models.TextField(verbose_name='Viesti')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kompomaatti.Event', verbose_name='Tapahtuma')),
            ],
            options={
                'verbose_name': 'irc-viesti',
                'verbose_name_plural': 'irc-viestit',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_start', models.DateTimeField(help_text='Viestin näyttäminen alkaa', verbose_name='Alkuaika')),
                ('show_end', models.DateTimeField(help_text='Viestin näyttäminen päättyy', verbose_name='Loppuaika')),
                ('text', models.TextField(help_text='Viestin leipäteksti. Katso ettei tästä tule liian pitkä.', verbose_name='Viesti')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kompomaatti.Event', verbose_name='Tapahtuma')),
            ],
            options={
                'verbose_name': 'viesti',
                'verbose_name_plural': 'viestit',
            },
        ),
        migrations.CreateModel(
            name='NPSong',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='Kappale')),
                ('artist', models.CharField(blank=True, max_length=255, verbose_name='Artisti')),
                ('time', models.DateTimeField(verbose_name='Aikaleima')),
                ('state', models.IntegerField(choices=[(0, 'Play'), (1, 'Stop')], verbose_name='Tila')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kompomaatti.Event', verbose_name='Tapahtuma')),
            ],
            options={
                'verbose_name': 'soitettava kappale',
                'verbose_name_plural': 'soitettavat kappaleet',
            },
        ),
        migrations.CreateModel(
            name='PlaylistVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Videon nimi tai otsikko.', max_length=64, verbose_name='Nimi')),
                ('url', models.URLField(help_text='Linkki Youtube-videoon.', verbose_name='Osoite')),
                ('index', models.IntegerField(help_text='Indeksi toistolistan järjestelemiseen. Pienimmällä numerolla varustetut toistetaan ensimmäiseksi.', verbose_name='Järjestysindeksi')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kompomaatti.Event', verbose_name='Tapahtuma')),
            ],
            options={
                'verbose_name': 'toistolistavideo',
                'verbose_name_plural': 'toistolistavideot',
            },
        ),
        migrations.CreateModel(
            name='ScreenConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enable_videos', models.BooleanField(default=True, help_text='Näytetäänkö esityksessä videoita playlistiltä.', verbose_name='Näytä videoita')),
                ('enable_twitter', models.BooleanField(default=True, help_text='Näytetäänkö esityksessä twittersyötteen sisältävä slaidi.', verbose_name='Näytä twitterfeed')),
                ('enable_irc', models.BooleanField(default=True, help_text='Näytetäänkö esityksessä irc-lokin sisältävä slaidi.', verbose_name='Näytä IRC')),
                ('video_interval', models.IntegerField(default=5, help_text='Kuinka usein videoita näytetään? Arvo annetaan minuuteissa. 0 = Joka kierroksella.', verbose_name='Videoiden näyttöväli')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='kompomaatti.Event', verbose_name='Tapahtuma')),
            ],
            options={
                'verbose_name': 'screenikonffi',
                'verbose_name_plural': 'screenikonffit',
            },
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Sponsorin nimi', max_length=64, verbose_name='Nimi')),
                ('logo', models.ImageField(blank=True, help_text='Sponsorin logo', upload_to='screen/sponsorlogos/', verbose_name='Kuva')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kompomaatti.Event', verbose_name='Tapahtuma')),
            ],
            options={
                'verbose_name': 'sponsori',
                'verbose_name_plural': 'sponsorit',
            },
        ),
    ]
