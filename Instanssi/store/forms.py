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

class StoreProductsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StoreProductsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        item_fields = Fieldset(u'', css_class='store-items')
        for item in StoreItem.items_available():
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
                    HTML('<a class="item-image fancybox" href="%s"><img src="%s" width="64" height="64" alt="Tuotekuva" /></a>' 
                         % (item.imagefile_original.url, item.imagefile_thumbnail.url)),
                )

            mdiv.fields.append(
                HTML(u'<span class="item-price">%d €/kpl</span>' % item.price)
            )
            mdiv.fields.append(name)
            item_fields.fields.append(mdiv)
            
        self.helper.layout = Layout(item_fields,)
        
    def _dataitems(self):
        for key, value in self.data.iteritems():
            try:
                if key.startswith('item-') and int(value):
                    yield (key[5:], int(value))
            except:
                continue

    def clean(self):
        cleaned_data = super(StoreProductsForm, self).clean()
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

        # Make sure we have at least SOME items in the order
        if not total_items:
            fails.append(u'Tilauksessa on oltava ainakin yksi tuote!')

        # Dump errors
        if fails:
            raise forms.ValidationError(fails)

        # All worked out, that's it
        return cleaned_data

class StoreInfoForm(forms.ModelForm):
    email_confirm = forms.EmailField(
        label=u'Vahvista sähköposti', max_length=255
    )

    def __init__(self, *args, **kwargs):
        super(StoreInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
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
            )
        )

    def clean(self):
        cleaned_data = super(StoreInfoForm, self).clean()
        fails = []

        # Make sure the email fields match
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

        # Dump errors
        if fails:
            raise forms.ValidationError(fails)

        # All worked out, that's it
        return cleaned_data

    class Meta:
        model = StoreTransaction
        exclude = ('time_created', 'time_paid', 'token', 'paid', 'key', 'status')
        
class StorePaymentMethodForm(forms.Form):
    read_terms = forms.BooleanField(
        label=u'Hyväksyn toimitusehdot', required=True
    )

    def __init__(self, *args, **kwargs):
        super(StorePaymentMethodForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        
        self.fields['read_terms'].help_text = \
            u'Olen lukenut <a href="%s" target="_blank">toimitusehdot</a> ' \
            u'ja hyväksyn ne. (Luethan myös <a href="%s" target="_blank">rekisteriselosteen</a>)' % (reverse('store:terms'), reverse('store:privacy'))

        self.helper.layout = Layout(
            Fieldset(
                u'Maksutavan valinta',
                'read_terms',
            )
        )
