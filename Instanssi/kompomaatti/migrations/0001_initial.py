# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Compo'
        db.create_table('kompomaatti_compo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('adding_end', self.gf('django.db.models.fields.DateTimeField')()),
            ('editing_end', self.gf('django.db.models.fields.DateTimeField')()),
            ('compo_start', self.gf('django.db.models.fields.DateTimeField')()),
            ('voting_start', self.gf('django.db.models.fields.DateTimeField')()),
            ('voting_end', self.gf('django.db.models.fields.DateTimeField')()),
            ('sizelimit', self.gf('django.db.models.fields.IntegerField')()),
            ('formats', self.gf('django.db.models.fields.CharField')(max_length='128')),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_voting_results', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('entry_view_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('kompomaatti', ['Compo'])

        # Adding model 'Entry'
        db.create_table('kompomaatti_entry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('compo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kompomaatti.Compo'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('creator', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('entryfile', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('imagefile_original', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('youtube_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('kompomaatti', ['Entry'])

        # Adding model 'Vote'
        db.create_table('kompomaatti_vote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('compo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kompomaatti.Compo'])),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kompomaatti.Entry'])),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('kompomaatti', ['Vote'])


    def backwards(self, orm):
        
        # Deleting model 'Compo'
        db.delete_table('kompomaatti_compo')

        # Deleting model 'Entry'
        db.delete_table('kompomaatti_entry')

        # Deleting model 'Vote'
        db.delete_table('kompomaatti_vote')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'kompomaatti.compo': {
            'Meta': {'object_name': 'Compo'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'adding_end': ('django.db.models.fields.DateTimeField', [], {}),
            'compo_start': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'editing_end': ('django.db.models.fields.DateTimeField', [], {}),
            'entry_view_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'formats': ('django.db.models.fields.CharField', [], {'max_length': "'128'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'show_voting_results': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sizelimit': ('django.db.models.fields.IntegerField', [], {}),
            'voting_end': ('django.db.models.fields.DateTimeField', [], {}),
            'voting_start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'kompomaatti.entry': {
            'Meta': {'object_name': 'Entry'},
            'compo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kompomaatti.Compo']"}),
            'creator': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'entryfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imagefile_original': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'youtube_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'kompomaatti.vote': {
            'Meta': {'object_name': 'Vote'},
            'compo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kompomaatti.Compo']"}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kompomaatti.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['kompomaatti']
