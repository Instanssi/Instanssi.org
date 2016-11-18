# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('kompomaatti', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='Lyhyt otsikko kommentille.', max_length=128, verbose_name='Otsikko', blank=True)),
                ('text', models.TextField(help_text='Kommenttiteksti.', verbose_name='Kommentti')),
                ('date', models.DateTimeField(verbose_name='Aika')),
            ],
            options={
                'verbose_name': 'kommentti',
                'verbose_name_plural': 'kommentit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BlogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='Lyhyt otsikko entrylle.', max_length=128, verbose_name='Otsikko')),
                ('text', models.TextField(verbose_name='Teksti')),
                ('date', models.DateTimeField(verbose_name='Aika')),
                ('public', models.BooleanField(default=False, help_text='Mik\xe4li entry on julkinen, tulee se n\xe4kyviin sek\xe4 tapahtuman sivuille ett\xe4 RSS-sy\xf6tteeseen.', verbose_name='Julkinen')),
                ('event', models.ForeignKey(verbose_name='Tapahtuma', to='kompomaatti.Event')),
                ('user', models.ForeignKey(verbose_name='K\xe4ytt\xe4j\xe4', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'entry',
                'verbose_name_plural': 'entryt',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='blogcomment',
            name='entry',
            field=models.ForeignKey(verbose_name='Entry', to='ext_blog.BlogEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blogcomment',
            name='user',
            field=models.ForeignKey(verbose_name='K\xe4ytt\xe4j\xe4', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
