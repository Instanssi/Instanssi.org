# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'BlogEntry.name'
        db.add_column('main2012_blogentry', 'name', self.gf('django.db.models.fields.CharField')(default='', max_length=64), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'BlogEntry.name'
        db.delete_column('main2012_blogentry', 'name')


    models = {
        'main2012.blogentry': {
            'Meta': {'object_name': 'BlogEntry'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['main2012']
