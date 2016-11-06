# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kompomaatti', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IRCMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(verbose_name='Aika')),
                ('nick', models.CharField(max_length=64, verbose_name='Nimimerkki')),
                ('message', models.TextField(verbose_name='Viesti')),
                ('event', models.ForeignKey(verbose_name='Tapahtuma', to='kompomaatti.Event')),
            ],
            options={
                'verbose_name': 'irc-viesti',
                'verbose_name_plural': 'irc-viestit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('show_start', models.DateTimeField(help_text='Viestin n\xe4ytt\xe4minen alkaa', verbose_name='Alkuaika')),
                ('show_end', models.DateTimeField(help_text='Viestin n\xe4ytt\xe4minen p\xe4\xe4ttyy', verbose_name='Loppuaika')),
                ('text', models.TextField(help_text='Viestin leip\xe4teksti. Katso ettei t\xe4st\xe4 tule liian pitk\xe4.', verbose_name='Viesti')),
                ('event', models.ForeignKey(verbose_name='Tapahtuma', to='kompomaatti.Event')),
            ],
            options={
                'verbose_name': 'viesti',
                'verbose_name_plural': 'viestit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NPSong',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='Kappale', blank=True)),
                ('artist', models.CharField(max_length=255, verbose_name='Artisti', blank=True)),
                ('time', models.DateTimeField(verbose_name='Aikaleima')),
                ('state', models.IntegerField(verbose_name='Tila', choices=[(0, 'Play'), (1, 'Stop')])),
                ('event', models.ForeignKey(verbose_name='Tapahtuma', to='kompomaatti.Event')),
            ],
            options={
                'verbose_name': 'soitettava kappale',
                'verbose_name_plural': 'soitettavat kappaleet',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlaylistVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Videon nimi tai otsikko.', max_length=64, verbose_name='Nimi')),
                ('url', models.URLField(help_text='Linkki Youtube-videoon.', verbose_name='Osoite')),
                ('index', models.IntegerField(help_text='Indeksi toistolistan j\xe4rjestelemiseen. Pienimm\xe4ll\xe4 numerolla varustetut toistetaan ensimm\xe4iseksi.', verbose_name='J\xc3\xa4rjestysindeksi')),
                ('event', models.ForeignKey(verbose_name='Tapahtuma', to='kompomaatti.Event')),
            ],
            options={
                'verbose_name': 'toistolistavideo',
                'verbose_name_plural': 'toistolistavideot',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScreenConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enable_videos', models.BooleanField(default=True, help_text='N\xe4ytet\xe4\xe4nk\xf6 esityksess\xe4 videoita playlistilt\xe4.', verbose_name='N\xe4yt\xe4 videoita')),
                ('enable_twitter', models.BooleanField(default=True, help_text='N\xe4ytet\xe4\xe4nk\xf6 esityksess\xe4 twittersy\xf6tteen sis\xe4lt\xe4v\xe4 slaidi.', verbose_name='N\xe4yt\xe4 twitterfeed')),
                ('enable_irc', models.BooleanField(default=True, help_text='N\xe4ytet\xe4\xe4nk\xf6 esityksess\xe4 irc-lokin sis\xe4lt\xe4v\xe4 slaidi.', verbose_name='N\xe4yt\xe4 IRC')),
                ('video_interval', models.IntegerField(default=5, help_text='Kuinka usein videoita n\xe4ytet\xe4\xe4n? Arvo annetaan minuuteissa. 0 = Joka kierroksella.', verbose_name='Videoiden n\xe4ytt\xf6v\xe4li')),
                ('event', models.ForeignKey(verbose_name='Tapahtuma', to='kompomaatti.Event', unique=True)),
            ],
            options={
                'verbose_name': 'screenikonffi',
                'verbose_name_plural': 'screenikonffit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Sponsorin nimi', max_length=64, verbose_name='Nimi')),
                ('logo', models.ImageField(help_text='Sponsorin logo', upload_to='screen/sponsorlogos/', verbose_name='Kuva', blank=True)),
                ('event', models.ForeignKey(verbose_name='Tapahtuma', to='kompomaatti.Event')),
            ],
            options={
                'verbose_name': 'sponsori',
                'verbose_name_plural': 'sponsorit',
            },
            bases=(models.Model,),
        ),
    ]
