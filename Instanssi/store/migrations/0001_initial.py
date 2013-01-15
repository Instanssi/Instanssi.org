# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StoreItem'
        db.create_table('store_storeitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('max', self.gf('django.db.models.fields.IntegerField')()),
            ('available', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('store', ['StoreItem'])

        # Adding model 'StoreTransaction'
        db.create_table('store_storetransaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=255)),
            ('telephone', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('postalcode', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('store', ['StoreTransaction'])

        # Adding model 'TransactionItem'
        db.create_table('store_transactionitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.StoreItem'])),
            ('transaction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.StoreTransaction'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('store', ['TransactionItem'])


    def backwards(self, orm):
        # Deleting model 'StoreItem'
        db.delete_table('store_storeitem')

        # Deleting model 'StoreTransaction'
        db.delete_table('store_storetransaction')

        # Deleting model 'TransactionItem'
        db.delete_table('store_transactionitem')


    models = {
        'store.storeitem': {
            'Meta': {'object_name': 'StoreItem'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'price': ('django.db.models.fields.FloatField', [], {})
        },
        'store.storetransaction': {
            'Meta': {'object_name': 'StoreTransaction'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'postalcode': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'store.transactionitem': {
            'Meta': {'object_name': 'TransactionItem'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['store.StoreItem']"}),
            'transaction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['store.StoreTransaction']"})
        }
    }

    complete_apps = ['store']