# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Tag'
        db.create_table('arkisto_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('arkisto', ['Tag'])

        # Adding model 'Event'
        db.create_table('arkisto_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('arkisto', ['Event'])

        # Adding model 'Compo'
        db.create_table('arkisto_compo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['arkisto.Event'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('arkisto', ['Compo'])

        # Adding model 'Entry'
        db.create_table('arkisto_entry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('compo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['arkisto.Compo'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('creator', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('youtube_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('arkisto', ['Entry'])

        # Adding M2M table for field tags on 'Entry'
        db.create_table('arkisto_entry_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm['arkisto.entry'], null=False)),
            ('tag', models.ForeignKey(orm['arkisto.tag'], null=False))
        ))
        db.create_unique('arkisto_entry_tags', ['entry_id', 'tag_id'])


    def backwards(self, orm):
        
        # Deleting model 'Tag'
        db.delete_table('arkisto_tag')

        # Deleting model 'Event'
        db.delete_table('arkisto_event')

        # Deleting model 'Compo'
        db.delete_table('arkisto_compo')

        # Deleting model 'Entry'
        db.delete_table('arkisto_entry')

        # Removing M2M table for field tags on 'Entry'
        db.delete_table('arkisto_entry_tags')


    models = {
        'arkisto.compo': {
            'Meta': {'object_name': 'Compo'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['arkisto.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'arkisto.entry': {
            'Meta': {'object_name': 'Entry'},
            'compo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['arkisto.Compo']"}),
            'creator': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['arkisto.Tag']", 'symmetrical': 'False'}),
            'youtube_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'arkisto.event': {
            'Meta': {'object_name': 'Event'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'arkisto.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['arkisto']
