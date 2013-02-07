# -*- coding: utf-8 -*-
# Forms for the Instanssi store.

import time
import random
import hashlib
import logging

from django import forms
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import \
    Submit, Layout, Fieldset, ButtonHolder, Hidden, Div, HTML
from Instanssi.store.models import StoreItem, TransactionItem, StoreTransaction

# Logger
logger = logging.getLogger(__name__)

# for creating ticket key hash
def gen_sha(text):
    h = hashlib.sha1()
    h.update(text)
    return h.hexdigest()

class StoreOrderForm(forms.ModelForm):
    """Displays an order form with items for a specific event listed."""

    email_confirm = forms.EmailField(
        label=u'Vahvista sähköposti', max_length=255
    )

    read_terms = forms.BooleanField(
        label=u'Hyväksyn toimitusehdot', required=True
    )

    def __init__(self, *args, **kwargs):
        self.event_id = kwargs.pop('event_id', None)
        super(StoreOrderForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'store'

        self.fields['read_terms'].help_text = \
            u'Olen lukenut <a href="%s" target="_blank">toimitusehdot</a> ' \
            u'ja hyväksyn ne. (Luethan myös <a href="%s" target="_blank">rekisteriselosteen</a>)' % (reverse('store:terms'), reverse('store:privacy'))

        self.fields['information'].widget.attrs['placeholder'] = \
            u'Mikäli tilauksessasi on T-paita, lisää tähän kenttään sen haluttu koko.'

        item_fields = Fieldset(u'', css_class='store-items')
        for item in StoreItem.items_for_event(self.event_id):
            name = 'item-%s' % item.id
            self.fields[name] = forms.IntegerField(
                initial=0, min_value=0, max_value=item.num_available(),
                label=u'%s' % (item.name),
                help_text=item.description, 
                required=False
            )
            
            # Set data-maxvalue attr for field, just for javascript stuff
            self.fields[name].widget.attrs['data-maxvalue'] = item.num_available()
            
            # Container
            mdiv = Div()
            
            # Print message if item is sold out
            if item.num_in_store() <= 0:
                self.fields[name].widget.attrs['disabled'] = True
                self.fields[name].label += u' <span class="item-soldout">(Lopussa)</span>'
            
            # Print img tag if item has image
            if item.imagefile_thumbnail:
                mdiv.fields.append(
                    HTML('<img class="item-image" src="%s" width="64" height="64" alt="Tuotakuva" data-bigimg="%s" />' 
                         % (item.imagefile_thumbnail.url, item.imagefile_original.url)),
                )

            mdiv.fields.append(
                HTML(u'<span class="item-price">%d €/kpl</span>' % item.price)
            )
            mdiv.fields.append(name)
            item_fields.fields.append(mdiv)

        self.helper.layout = Layout(
            HTML(u'<h2>Tuotteet</h2>'),
            item_fields,
            HTML(u'<h2>Maksajan tiedot</h2>'),
            Fieldset(
                u'',
                'firstname',
                'lastname',
                'email',
                'email_confirm',
                'telephone',
                'mobile',
                'company',
                'street',
                'postalcode',
                'city',
                'country',
                'information',
                'read_terms',
                ButtonHolder(
                    Submit('Buy', u'Osta')
                ),
                css_class='store-details'
            )
        )

    def _dataitems(self):
        for key, value in self.data.iteritems():
            try:
                if key.startswith('item-') and int(value):
                    yield (key[5:], int(value))
            except:
                continue

    def clean(self):
        cleaned_data = super(StoreOrderForm, self).clean()
        total_items = 0

        fails = []

        # also check that the purchase amount for each field makes sense
        for (item_id, amount) in self._dataitems():
            store_item = StoreItem.objects.get(id=int(item_id))
            total_items += amount
            if store_item.num_available() < amount:
                fails.append(
                    u'Tuotetta "%s" ei ole saatavilla riittävästi!'
                    % store_item.name
                )

        if not total_items:
            fails.append(u'Tilauksessa on oltava ainakin yksi tuote!')

        if 'email' in self.data and 'email_confirm' in self.data:
            if self.data['email'] != self.data['email_confirm']:
                if not 'email_confirm' in self._errors:
                    self._errors['email_confirm'] = self.error_class()
                self._errors['email_confirm'].append(
                    u'Osoitteet eivät täsmää!'
                )
                fails.append(
                    u'Vahvista sähköpostiosoitteesi kirjoittamalla sama '
                    u'osoite molempiin kenttiin!'
                )

        if fails:
            raise forms.ValidationError(fails)

        return cleaned_data

    def save(self, commit=True):
        """Saves a store transaction form, also generating TransactionItems
        for each item in the post data."""

        new_transaction = super(StoreOrderForm, self).save(commit=False)

        for i in range(10):
            try:
                str = u'%s|%s|%s|%s|%s|%s' % (i, new_transaction.firstname, new_transaction.lastname, time.time(), random.random(), random.random())
                new_transaction.key = gen_sha(str.encode('utf-8'))
                new_transaction.save()
                break
            except IntegrityError as ex:
                logger.warning("SHA-1 Collision in transaction (WTF!) Key: %s, exception: %s." % (ta.key, ex))

        
        transaction_items = []
        for (item_id, amount) in self._dataitems():
            if amount > 0:
                store_item = StoreItem.objects.get(id=int(item_id))
                new_item = TransactionItem(
                    item=store_item,
                    transaction=new_transaction,
                    amount=amount
                )
                new_item.save()
                transaction_items.append(new_item)

        return new_transaction

    class Meta:
        model = StoreTransaction
        exclude = ('time_created', 'time_paid', 'token', 'paid', 'key', 'status')
