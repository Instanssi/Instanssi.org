# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Kilpailun nimi (max 32 merkki\xe4).', max_length=32, verbose_name='Nimi')),
                ('description', models.TextField(verbose_name='Kuvaus')),
                ('participation_end', models.DateTimeField(help_text='T\xe4m\xe4n j\xe4lkeen kilpailuun ei voi en\xe4\xe4 osallistua.', verbose_name='Deadline osallistumiselle.')),
                ('start', models.DateTimeField(help_text='Kilpailun aloitusaika.', verbose_name='Kilpailun alku')),
                ('end', models.DateTimeField(help_text='Kilpailun p\xe4\xe4ttymisaika.', null=True, verbose_name='Kilpailun loppu', blank=True)),
                ('score_type', models.CharField(help_text='Pisteiden tyyppi (km, m, sek, ...). Maksimipituus 8 merkki\xe4.', max_length=8, verbose_name='Pisteiden tyyppi')),
                ('score_sort', models.IntegerField(default=0, help_text='Onko suurimman vai pienimm\xe4n tuloksen saavuttanut voittaja?', verbose_name='Pisteiden j\xe4rjestely', choices=[(0, 'Korkein tulos ensin'), (1, 'Matalin tulos ensin')])),
                ('show_results', models.BooleanField(default=False, help_text='N\xe4yt\xe4 kilpailun tulokset.', verbose_name='N\xe4yt\xe4 tulokset')),
                ('active', models.BooleanField(default=True, help_text='Onko kilpailu aktiivinen, eli n\xe4ytet\xe4\xe4nk\xf6 se kompomaatissa kaikille.', verbose_name='Aktiivinen')),
                ('hide_from_archive', models.BooleanField(default=False, help_text='Piilotetaanko kilpailun tulokset arkistosta ? T\xe4m\xe4 ylikirjoittaa eventin asetuksen.', verbose_name='Piilotus arkistosta')),
            ],
            options={
                'verbose_name': 'kilpailu',
                'verbose_name_plural': 'kilpailut',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompetitionParticipation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('participant_name', models.CharField(default='', help_text='Nimimerkki jolla haluat osallistua.', max_length=32, verbose_name='Osallistujan nimi')),
                ('score', models.FloatField(default=0, help_text='Kilpailijan saavuttamat pisteet', verbose_name='Pisteet', blank=True)),
                ('disqualified', models.BooleanField(default=False, help_text='Suoritus on diskattu s\xe4\xe4nt\xf6rikon tai teknisten virheiden takia.', verbose_name='Diskattu')),
                ('disqualified_reason', models.TextField(verbose_name='Diskauksen syy', blank=True)),
                ('competition', models.ForeignKey(verbose_name='Kilpailu', to='kompomaatti.Competition', help_text='Kilpailu johon osallistuttu')),
                ('user', models.ForeignKey(verbose_name='K\xe4ytt\xe4j\xe4', to=settings.AUTH_USER_MODEL, help_text='Osallistuja')),
            ],
            options={
                'verbose_name': 'ilmoittautuminen',
                'verbose_name_plural': 'ilmoittautumiset',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Compo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Kompon nimi (max 32 merkki\xe4).', max_length=32, verbose_name='Nimi')),
                ('description', models.TextField(verbose_name='Kuvaus')),
                ('adding_end', models.DateTimeField(help_text='T\xe4m\xe4n j\xe4lkeen kompoon ei voi en\xe4\xe4 l\xe4hett\xe4\xe4 uusia entryj\xe4. Muokkaus toimii viel\xe4.', verbose_name='Deadline entryjen lis\xe4yksille')),
                ('editing_end', models.DateTimeField(help_text='T\xe4m\xe4n j\xe4lkeen entryjen tiedostoja tai muita tietoja ei voi en\xe4\xe4 muokata.', verbose_name='Deadline entryjen muokkauksille')),
                ('compo_start', models.DateTimeField(help_text='Kompon alkamisaika tapahtumassa (tapahtumakalenteria varten).', verbose_name='Kompon aloitusaika')),
                ('voting_start', models.DateTimeField(help_text='Alkamisaika entryjen \xe4\xe4nestykselle.', verbose_name='\xc4\xe4nestyksen alkamisaika')),
                ('voting_end', models.DateTimeField(help_text='P\xe4\xe4ttymisaika entryjen \xe4\xe4nestykselle.', verbose_name='\xc4\xe4nestyksen p\xe4\xe4ttymisaika')),
                ('entry_sizelimit', models.IntegerField(default=134217728, help_text='Kokoraja entrytiedostoille (tavua).', verbose_name='Kokoraja entryille')),
                ('source_sizelimit', models.IntegerField(default=134217728, help_text='Kokoraja sorsatiedostoille (tavua).', verbose_name='Kokoraja sorsille')),
                ('formats', models.CharField(default=b'zip|7z|gz|bz2', help_text='Entrypaketille sallitut tiedostop\xe4\xe4tteet pystyviivalla eroteltuna, esim. "png|jpg".', max_length=128, verbose_name='Sallitut tiedostop\xe4\xe4tteet')),
                ('source_formats', models.CharField(default=b'zip|7z|gz|bz2', help_text='Entryn l\xe4hdekoodipaketille sallitut tiedostop\xe4\xe4tteet pystyviivalla eroteltuna', max_length=128, verbose_name='Sallitut l\xe4hdekoodipaketin p\xe4\xe4tteet')),
                ('image_formats', models.CharField(default=b'png|jpg', help_text='Entryn pikkukuvalle sallitut tiedostop\xe4\xe4tteet pystyviivalla eroteltuna', max_length=128, verbose_name='Sallitut kuvatiedoston p\xe4\xe4tteet')),
                ('active', models.BooleanField(default=True, help_text='Onko kompo aktiivinen, eli n\xe4ytet\xe4\xe4nk\xf6 se kompomaatissa kaikille.', verbose_name='Aktiivinen')),
                ('show_voting_results', models.BooleanField(default=False, help_text='N\xe4yt\xe4 \xe4\xe4nestustulokset.', verbose_name='N\xe4yt\xe4 tulokset')),
                ('entry_view_type', models.IntegerField(default=0, help_text='Ilmoittaa millainen n\xe4kym\xe4 n\xe4ytet\xe4\xe4n entryn tiedoissa. Latauslinkki n\xe4ytet\xe4\xe4n aina.', verbose_name='Entryesittely', choices=[(0, 'Ei mit\xe4\xe4n'), (1, 'Youtube ensin, sitten kuva'), (2, 'Vain kuva'), (3, '(deprecated)')])),
                ('hide_from_archive', models.BooleanField(default=False, help_text='Piilottaa kompon tulokset arkistosta. T\xe4m\xe4 asetus ohittaa tapahtuman tiedoissa valitun asetuksen.', verbose_name='Piilotus arkistosta')),
                ('hide_from_frontpage', models.BooleanField(default=False, help_text='Piilottaa kompon nimen ja kuvauksen tapahtuman etusivulta. K\xe4yt\xe4 esim. jos kompon kuvaus on viel\xe4 suunnitteilla.', verbose_name='Piilotus etusivulta')),
                ('is_votable', models.BooleanField(default=True, help_text='Teosta voi ylip\xe4\xe4t\xe4\xe4n \xe4\xe4nest\xe4\xe4 (Pois esim. robocodelle).', verbose_name='\xc4\xe4nestett\xe4viss\xe4')),
                ('thumbnail_pref', models.IntegerField(default=2, help_text='Pikkukuvan luonti ja asettaminen.', verbose_name='Pikkukuvan asetukset', choices=[(0, 'Vaadi erillinen pikkukuva.'), (1, 'K\xe4yt\xe4 pikkukuvana teoksen tiedostoa (Toimii vain png/jpg-tiedostoille).'), (2, 'Salli pikkukuva (ei vaadittu).'), (3, '\xc4l\xe4 salli pikkukuvaa.')])),
            ],
            options={
                'verbose_name': 'kompo',
                'verbose_name_plural': 'kompot',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Nimi tuotokselle', max_length=64, verbose_name='Nimi')),
                ('description', models.TextField(help_text='Voi sis\xe4lt\xe4\xe4 mm. tietoja k\xe4ytetyist\xe4 tekniikoista, muuta sanottavaa.', verbose_name='Kuvaus')),
                ('creator', models.CharField(help_text='Tuotoksen tekij\xe4n tai tekij\xe4ryhm\xe4n nimi', max_length=64, verbose_name='Tekij\xe4')),
                ('entryfile', models.FileField(help_text='Tuotospaketti.', upload_to=b'kompomaatti/entryfiles/', verbose_name='Tiedosto')),
                ('sourcefile', models.FileField(help_text='L\xe4hdekoodipaketti.', upload_to=b'kompomaatti/entrysources/', verbose_name='L\xe4hdekoodi', blank=True)),
                ('imagefile_original', models.ImageField(help_text='Edustava kuva teokselle. Ei pakollinen, mutta suositeltava.', upload_to=b'kompomaatti/entryimages/', verbose_name='Kuva', blank=True)),
                ('youtube_url', models.URLField(help_text='Linkki teoksen Youtube-videoon.', verbose_name='Youtube URL', blank=True)),
                ('disqualified', models.BooleanField(default=False, help_text='Entry on diskattu s\xe4\xe4nt\xf6rikon tai teknisten ongelmien takia. DISKAUS ON TEHT\xc4V\xc4 ENNEN \xc4\xc4NESTYKSEN ALKUA!', verbose_name='Diskattu')),
                ('disqualified_reason', models.TextField(help_text='Diskauksen syy.', verbose_name='Syy diskaukseen', blank=True)),
                ('archive_score', models.FloatField(help_text='Arkistoidun entryn kompossa saamat pisteet. Mik\xe4li t\xe4t\xe4 ei m\xe4\xe4ritet\xe4, lasketaan pisteet suoraan \xe4\xe4nestystuloksista.', null=True, verbose_name='Pisteet', blank=True)),
                ('archive_rank', models.IntegerField(help_text='Arkistoidun entryn kompossa saama sijoitus. T\xe4m\xe4 voidaan laskea my\xf6s pistem\xe4\xe4rist\xe4 automaattisesti.', null=True, verbose_name='Sijoitus', blank=True)),
                ('compo', models.ForeignKey(verbose_name='kompo', to='kompomaatti.Compo', help_text='Kompo johon osallistutaan')),
                ('user', models.ForeignKey(verbose_name='k\xe4ytt\xe4j\xe4', to=settings.AUTH_USER_MODEL, help_text='K\xe4ytt\xe4j\xe4 jolle entry kuuluu')),
            ],
            options={
                'verbose_name': 'tuotos',
                'verbose_name_plural': 'tuotokset',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Tapahtuman nimi', unique=True, max_length=64, verbose_name='Nimi')),
                ('date', models.DateField(help_text='Tapahtuman p\xe4iv\xe4m\xe4\xe4r\xe4 (alku)', verbose_name='P\xe4iv\xe4m\xe4\xe4r\xe4')),
                ('archived', models.BooleanField(default=False, help_text='Saa n\xe4ytt\xe4\xe4 arkistossa', verbose_name='Arkistoitu')),
                ('mainurl', models.URLField(help_text='URL Tapahtuman p\xe4\xe4sivustolle', verbose_name='Tapahtuman p\xe4\xe4sivu', blank=True)),
            ],
            options={
                'verbose_name': 'tapahtuma',
                'verbose_name_plural': 'tapahtumat',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('otherinfo', models.TextField(help_text='Muita yhteystietoja, mm. IRC-tunnus (verkon kera), jne.', verbose_name='Muut yhteystiedot')),
                ('user', models.ForeignKey(verbose_name='K\xe4ytt\xe4j\xe4', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'profiili',
                'verbose_name_plural': 'profiilit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rank', models.IntegerField(verbose_name='Sijoitus')),
                ('compo', models.ForeignKey(verbose_name='kompo', to='kompomaatti.Compo')),
                ('entry', models.ForeignKey(verbose_name='tuotos', to='kompomaatti.Entry')),
                ('user', models.ForeignKey(verbose_name='k\xe4ytt\xe4j\xe4', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\xe4\xe4ni',
                'verbose_name_plural': '\xe4\xe4net',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VoteCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text='\xc4\xe4nestysavain.', unique=True, max_length=64, verbose_name='Avain')),
                ('time', models.DateTimeField(help_text='Aika jolloin avain assosioitiin k\xe4ytt\xe4j\xe4lle.', null=True, verbose_name='Aikaleima', blank=True)),
                ('associated_to', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text='K\xe4ytt\xe4j\xe4 jolle avain on assosioitu', null=True, verbose_name='K\xe4ytt\xe4j\xe4')),
                ('event', models.ForeignKey(blank=True, to='kompomaatti.Event', help_text='Tapahtuma, johon \xe4\xe4nestysavain on assosioitu', null=True, verbose_name='Tapahtuma')),
            ],
            options={
                'verbose_name': '\xe4\xe4nestysavain',
                'verbose_name_plural': '\xe4\xe4nestysavaimet',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VoteCodeRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(help_text='Lyhyt aneluteksti admineille :)', verbose_name='Kuvaus')),
                ('event', models.ForeignKey(verbose_name='Tapahtuma', to='kompomaatti.Event', help_text='Tapahtuma, johon \xe4\xe4nestysoikeutta pyydet\xe4\xe4n', null=True)),
                ('user', models.ForeignKey(verbose_name='K\xe4ytt\xe4j\xe4', to=settings.AUTH_USER_MODEL, help_text='Pyynn\xf6n esitt\xe4nyt k\xe4ytt\xe4j\xe4', unique=True)),
            ],
            options={
                'verbose_name': '\xe4\xe4nestyskoodipyynt\xf6',
                'verbose_name_plural': '\xe4\xe4nestyskoodipyynn\xf6t',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='votecode',
            unique_together=set([('event', 'key'), ('event', 'associated_to')]),
        ),
        migrations.AddField(
            model_name='compo',
            name='event',
            field=models.ForeignKey(verbose_name='tapahtuma', to='kompomaatti.Event', help_text='Tapahtuma johon kompo kuuluu'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='competition',
            name='event',
            field=models.ForeignKey(verbose_name='Tapahtuma', to='kompomaatti.Event', help_text='Tapahtuma johon kilpailu kuuluu'),
            preserve_default=True,
        ),
    ]
