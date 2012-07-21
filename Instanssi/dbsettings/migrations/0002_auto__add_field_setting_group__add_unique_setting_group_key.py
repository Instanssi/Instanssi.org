# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Setting.group'
        db.add_column('dbsettings_setting', 'group',
                      self.gf('django.db.models.fields.CharField')(default=u'', max_length=32),
                      keep_default=False)

        # Adding unique constraint on 'Setting', fields ['group', 'key']
        db.create_unique('dbsettings_setting', ['group', 'key'])


    def backwards(self, orm):
        # Removing unique constraint on 'Setting', fields ['group', 'key']
        db.delete_unique('dbsettings_setting', ['group', 'key'])

        # Deleting field 'Setting.group'
        db.delete_column('dbsettings_setting', 'group')


    models = {
        'dbsettings.setting': {
            'Meta': {'unique_together': "(('key', 'group'),)", 'object_name': 'Setting'},
            'group': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['dbsettings']