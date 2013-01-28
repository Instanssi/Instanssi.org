# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Ticket.owner_firstname'
        db.add_column('tickets_ticket', 'owner_firstname',
                      self.gf('django.db.models.fields.CharField')(default=u'', max_length=64),
                      keep_default=False)

        # Adding field 'Ticket.owner_lastname'
        db.add_column('tickets_ticket', 'owner_lastname',
                      self.gf('django.db.models.fields.CharField')(default=u'', max_length=64),
                      keep_default=False)

        # Adding field 'Ticket.owner_email'
        db.add_column('tickets_ticket', 'owner_email',
                      self.gf('django.db.models.fields.CharField')(default=u'', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Ticket.owner_firstname'
        db.delete_column('tickets_ticket', 'owner_firstname')

        # Deleting field 'Ticket.owner_lastname'
        db.delete_column('tickets_ticket', 'owner_lastname')

        # Deleting field 'Ticket.owner_email'
        db.delete_column('tickets_ticket', 'owner_email')


    models = {
        'kompomaatti.event': {
            'Meta': {'object_name': 'Event'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mainurl': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'store.storeitem': {
            'Meta': {'object_name': 'StoreItem'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'delivery_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kompomaatti.Event']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imagefile_original': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max': ('django.db.models.fields.IntegerField', [], {}),
            'max_per_order': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'price': ('django.db.models.fields.FloatField', [], {})
        },
        'store.storetransaction': {
            'Meta': {'object_name': 'StoreTransaction'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'country': ('django_countries.fields.CountryField', [], {'default': "'FI'", 'max_length': '2'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'postalcode': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_paid': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'tickets.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kompomaatti.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'owner_email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner_firstname': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'owner_lastname': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'storeitem': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['store.StoreItem']"}),
            'transaction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['store.StoreTransaction']", 'null': 'True', 'blank': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['tickets']