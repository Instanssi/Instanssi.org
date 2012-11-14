# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IRCMessage'
        db.create_table('screenshow_ircmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kompomaatti.Event'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('nick', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('screenshow', ['IRCMessage'])


    def backwards(self, orm):
        # Deleting model 'IRCMessage'
        db.delete_table('screenshow_ircmessage')


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
        'screenshow.sponsor': {
            'Meta': {'object_name': 'Sponsor'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kompomaatti.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['screenshow']