# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('kompomaatti', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Tuotteen lyhyt nimi.', max_length=255, verbose_name='Tuotteen nimi')),
                ('description', models.TextField(help_text='Tuotteen pitk\xe4 kuvaus.', verbose_name='Tuotteen kuvaus')),
                ('price', models.IntegerField(help_text='Tuotteen hinta euroissa.', verbose_name='Tuotteen hinta')),
                ('max', models.IntegerField(help_text='Kuinka monta kappaletta on ostettavissa ennen myynnin lopettamista.', verbose_name='Kappaletta saatavilla')),
                ('available', models.BooleanField(default=False, help_text='Ilmoittaa, n\xe4kyyk\xf6 tuote kaupassa.', verbose_name='Ostettavissa')),
                ('imagefile_original', models.ImageField(help_text='Edustava kuva tuotteelle.', upload_to=b'store/images/', null=True, verbose_name='Tuotekuva', blank=True)),
                ('max_per_order', models.IntegerField(default=10, help_text='Kuinka monta kappaletta voidaan ostaa kerralla.', verbose_name='Maksimi per tilaus')),
                ('sort_index', models.IntegerField(default=0, help_text='Tuotteet esitet\xe4\xe4n kaupassa t\xe4m\xe4n luvun mukaan j\xe4rjestettyn\xe4, pienempilukuiset ensin.', verbose_name='J\xe4rjestysarvo')),
                ('event', models.ForeignKey(blank=True, to='kompomaatti.Event', help_text='Tapahtuma johon tuote liittyy.', null=True, verbose_name='Tapahtuma')),
            ],
            options={
                'verbose_name': 'tuote',
                'verbose_name_plural': 'tuotteet',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoreTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(help_text='Maksupalvelun maksukohtainen tunniste', max_length=255, verbose_name='Palvelutunniste')),
                ('time_created', models.DateTimeField(null=True, verbose_name='Luontiaika', blank=True)),
                ('time_paid', models.DateTimeField(null=True, verbose_name='Maksun varmistumisaika', blank=True)),
                ('time_pending', models.DateTimeField(null=True, verbose_name='Maksun maksuaika', blank=True)),
                ('time_cancelled', models.DateTimeField(null=True, verbose_name='Peruutusaika', blank=True)),
                ('payment_method_name', models.CharField(default='', help_text='Tapa jolla tilaus maksettiin', max_length=32, verbose_name='Maksutapa', blank=True)),
                ('key', models.CharField(help_text='Paikallinen maksukohtainen tunniste', unique=True, max_length=40, verbose_name='Avain')),
                ('firstname', models.CharField(max_length=64, verbose_name='Etunimi')),
                ('lastname', models.CharField(max_length=64, verbose_name='Sukunimi')),
                ('company', models.CharField(max_length=128, verbose_name='Yritys', blank=True)),
                ('email', models.EmailField(help_text='S\xe4hk\xf6postiosoitteen on oltava toimiva, sill\xe4 liput ja tuotteiden lunastukseen tarvittavat koodit l\xe4hetet\xe4\xe4n sinne.', max_length=255, verbose_name='S\xe4hk\xf6posti')),
                ('telephone', models.CharField(max_length=64, verbose_name='Puhelinnumero', blank=True)),
                ('mobile', models.CharField(max_length=64, verbose_name='Matkapuhelin', blank=True)),
                ('street', models.CharField(help_text='Katusoite tarvitaan maksupalvelun vaatimuksesta.', max_length=128, verbose_name='Katuosoite')),
                ('postalcode', models.CharField(max_length=16, verbose_name='Postinumero')),
                ('city', models.CharField(max_length=64, verbose_name='Postitoimipaikka')),
                ('country', django_countries.fields.CountryField(default=b'FI', max_length=2, verbose_name='Maa')),
                ('information', models.TextField(help_text='Mik\xe4li tilaukseen kuuluu T-paitoja, m\xe4\xe4rit\xe4 niiden koot t\xe4ss\xe4.', verbose_name='Lis\xe4tiedot', blank=True)),
            ],
            options={
                'verbose_name': 'transaktio',
                'verbose_name_plural': 'transaktiot',
                'permissions': (('view_storetransaction', 'Can view store transactions'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TransactionItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text='Lippuavain', unique=True, max_length=40, verbose_name='Avain')),
                ('time_delivered', models.DateTimeField(null=True, verbose_name='Toimitusaika', blank=True)),
                ('purchase_price', models.IntegerField(help_text='Tuotteen hinta euroissa ostoshetkell\xe4.', verbose_name='Tuotteen hinta')),
                ('item', models.ForeignKey(verbose_name='Tuote', to='store.StoreItem')),
                ('transaction', models.ForeignKey(verbose_name='Ostotapahtuma', to='store.StoreTransaction')),
            ],
            options={
                'verbose_name': 'transaktiotuote',
                'verbose_name_plural': 'transaktiotuotteet',
            },
            bases=(models.Model,),
        ),
    ]
