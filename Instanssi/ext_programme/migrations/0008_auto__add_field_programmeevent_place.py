# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ProgrammeEvent.place'
        db.add_column(u'ext_programme_programmeevent', 'place',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ProgrammeEvent.place'
        db.delete_column(u'ext_programme_programmeevent', 'place')


    models = {
        u'ext_programme.programmeevent': {
            'Meta': {'object_name': 'ProgrammeEvent'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kompomaatti.Event']"}),
            'event_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'facebook_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'github_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'gplus_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'icon2_original': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'icon_original': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linkedin_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'presenters': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'presenters_titles': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'twitter_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'wiki_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'kompomaatti.event': {
            'Meta': {'object_name': 'Event'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mainurl': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        }
    }

    complete_apps = ['ext_programme']