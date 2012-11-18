# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ScreenConfig'
        db.create_table('screenshow_screenconfig', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kompomaatti.Event'])),
            ('enable_videos', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('enable_twitter', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('enable_irc', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('video_interval', self.gf('django.db.models.fields.IntegerField')(default=5)),
        ))
        db.send_create_signal('screenshow', ['ScreenConfig'])


    def backwards(self, orm):
        # Deleting model 'ScreenConfig'
        db.delete_table('screenshow_screenconfig')


    models = {
        'kompomaatti.event': {
            'Meta': {'object_name': 'Event'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mainurl': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'screenshow.ircmessage': {
            'Meta': {'object_name': 'IRCMessage'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kompomaatti.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'nick': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'screenshow.message': {
            'Meta': {'object_name': 'Message'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kompomaatti.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show_end': ('django.db.models.fields.DateTimeField', [], {}),
            'show_start': ('django.db.models.fields.DateTimeField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'screenshow.playlistvideo': {
            'Meta': {'object_name': 'PlaylistVideo'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kompomaatti.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'64'"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'screenshow.screenconfig': {
            'Meta': {'object_name': 'ScreenConfig'},
            'enable_irc': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'enable_twitter': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'enable_videos': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kompomaatti.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'video_interval': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'screenshow.sponsor': {
            'Meta': {'object_name': 'Sponsor'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kompomaatti.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['screenshow']