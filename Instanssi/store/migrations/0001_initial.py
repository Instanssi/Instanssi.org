# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-11 17:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('kompomaatti', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=256, verbose_name='Aihe')),
                ('mail_to', models.CharField(max_length=256, verbose_name='Vastaanottajan osoite')),
                ('mail_from', models.CharField(max_length=256, verbose_name='Lähettäjän osoite')),
                ('sent', models.DateTimeField(default=None, null=True, verbose_name='Lähetysaika')),
                ('params', models.TextField(default=None, null=True, verbose_name='Lähetysparametrit')),
                ('content', models.TextField(default=None, null=True, verbose_name='Kuitin sisältö')),
            ],
            options={
                'verbose_name': 'kuitti',
                'verbose_name_plural': 'kuitit',
            },
        ),
        migrations.CreateModel(
            name='StoreItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Tuotteen lyhyt nimi.', max_length=255, verbose_name='Tuotteen nimi')),
                ('description', models.TextField(help_text='Tuotteen pitkä kuvaus.', verbose_name='Tuotteen kuvaus')),
                ('price', models.DecimalField(decimal_places=2, help_text='Tuotteen hinta.', max_digits=5, verbose_name='Tuotteen hinta')),
                ('max', models.IntegerField(help_text='Kuinka monta kappaletta on ostettavissa ennen myynnin lopettamista.', verbose_name='Kappaletta saatavilla')),
                ('available', models.BooleanField(default=False, help_text='Ilmoittaa, näkyykö tuote kaupassa.', verbose_name='Ostettavissa')),
                ('imagefile_original', models.ImageField(blank=True, help_text='Edustava kuva tuotteelle.', null=True, upload_to='store/images/', verbose_name='Tuotekuva')),
                ('max_per_order', models.IntegerField(default=10, help_text='Kuinka monta kappaletta voidaan ostaa kerralla.', verbose_name='Maksimi per tilaus')),
                ('sort_index', models.IntegerField(default=0, help_text='Tuotteet esitetään kaupassa tämän luvun mukaan järjestettynä, pienempilukuiset ensin.', verbose_name='Järjestysarvo')),
                ('discount_amount', models.IntegerField(default=-1, help_text='Pienin määrä tuotteita joka oikeuttaa alennukseen (-1 = ei mitään)', verbose_name='Alennusmäärä')),
                ('discount_percentage', models.IntegerField(default=0, help_text='Alennuksen määrä prosentteina kun tuotteiden määrä saavuttaa alennusmäärän.', verbose_name='Alennusprosentti')),
                ('is_ticket', models.BooleanField(default=False, help_text='Tuote on lipputuote, ja sitä voi käyttää esim. kompomaatissa äänestysoikeuden hankkimiseen', verbose_name='Tuote on lipputuote')),
                ('event', models.ForeignKey(blank=True, help_text='Tapahtuma johon tuote liittyy.', null=True, on_delete=django.db.models.deletion.CASCADE, to='kompomaatti.Event', verbose_name='Tapahtuma')),
            ],
            options={
                'verbose_name': 'tuote',
                'verbose_name_plural': 'tuotteet',
            },
        ),
        migrations.CreateModel(
            name='StoreItemVariant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Tuotevariantin nimi')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.StoreItem')),
            ],
            options={
                'verbose_name': 'tuotevariantti',
                'verbose_name_plural': 'tuotevariantit',
            },
        ),
        migrations.CreateModel(
            name='StoreTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(help_text='Maksupalvelun maksukohtainen tunniste', max_length=255, verbose_name='Palvelutunniste')),
                ('time_created', models.DateTimeField(blank=True, null=True, verbose_name='Luontiaika')),
                ('time_paid', models.DateTimeField(blank=True, null=True, verbose_name='Maksun varmistumisaika')),
                ('time_pending', models.DateTimeField(blank=True, null=True, verbose_name='Maksun maksuaika')),
                ('time_cancelled', models.DateTimeField(blank=True, null=True, verbose_name='Peruutusaika')),
                ('payment_method_name', models.CharField(blank=True, default='', help_text='Tapa jolla tilaus maksettiin', max_length=32, verbose_name='Maksutapa')),
                ('key', models.CharField(help_text='Paikallinen maksukohtainen tunniste', max_length=40, unique=True, verbose_name='Avain')),
                ('firstname', models.CharField(max_length=64, verbose_name='Etunimi')),
                ('lastname', models.CharField(max_length=64, verbose_name='Sukunimi')),
                ('company', models.CharField(blank=True, max_length=128, verbose_name='Yritys')),
                ('email', models.EmailField(help_text='Sähköpostiosoitteen on oltava toimiva, sillä liput ja tuotteiden lunastukseen tarvittavat koodit lähetetään sinne.', max_length=255, verbose_name='Sähköposti')),
                ('telephone', models.CharField(blank=True, max_length=64, verbose_name='Puhelinnumero')),
                ('mobile', models.CharField(blank=True, max_length=64, verbose_name='Matkapuhelin')),
                ('street', models.CharField(help_text='Katusoite tarvitaan maksupalvelun vaatimuksesta.', max_length=128, verbose_name='Katuosoite')),
                ('postalcode', models.CharField(max_length=16, verbose_name='Postinumero')),
                ('city', models.CharField(max_length=64, verbose_name='Postitoimipaikka')),
                ('country', django_countries.fields.CountryField(default='FI', max_length=2, verbose_name='Maa')),
                ('information', models.TextField(blank=True, help_text='Mikäli tilaukseen kuuluu T-paitoja, määritä niiden koot tässä.', verbose_name='Lisätiedot')),
            ],
            options={
                'verbose_name': 'transaktio',
                'verbose_name_plural': 'transaktiot',
                'permissions': (('view_storetransaction', 'Can view store transactions'),),
            },
        ),
        migrations.CreateModel(
            name='TransactionItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text='Lippuavain', max_length=40, unique=True, verbose_name='Avain')),
                ('time_delivered', models.DateTimeField(blank=True, null=True, verbose_name='Toimitusaika')),
                ('purchase_price', models.DecimalField(decimal_places=2, help_text='Tuotteen hinta ostoshetkellä', max_digits=5, verbose_name='Tuotteen hinta')),
                ('original_price', models.DecimalField(decimal_places=2, help_text='Tuotteen hinta ostoshetkellä ilman alennuksia', max_digits=5, verbose_name='Tuotteen alkuperäinen hinta')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.StoreItem', verbose_name='Tuote')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.StoreTransaction', verbose_name='Ostotapahtuma')),
                ('variant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.StoreItemVariant', verbose_name='Tuotevariantti')),
            ],
            options={
                'verbose_name': 'transaktiotuote',
                'verbose_name_plural': 'transaktiotuotteet',
            },
        ),
    ]
