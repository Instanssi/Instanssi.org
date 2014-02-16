# -*- coding: utf-8 -*-
# Forms for the Instanssi store.

import time
import random
import hashlib
import logging

from django import forms
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.utils.html import format_html

from Instanssi.store.models import StoreTransaction, TransactionItem, StoreItem

# Logger
logger = logging.getLogger(__name__)

# for creating ticket key hash
def gen_sha(text):
    h = hashlib.sha1()
    h.update(text)
    return h.hexdigest()

class ProductWidget(forms.NumberInput):
    def __init__(self, attrs=None):
        self.large_image = attrs.pop('large_image')
        self.small_image = attrs.pop('small_image')
        self.price = attrs.pop('price')
        self.available = attrs.pop('available')
        super(ProductWidget, self).__init__(attrs)
    
    def render(self, name, value, attrs=None):
        num_field = super(ProductWidget, self).render(name, value, attrs)
        
        # Form HTML for sold out field
        available_html = u''
        if self.available <= 0:
            available_html = u'<div class="item-soldout">(Lopussa)</div>\n'
        
        # Form final HTML
        return format_html('\n\
            <div class="item-image">\n\
                <a class="item-fancybox" href="{0}">\n\
                    <img src="{1}" width="64" height="64" alt="Tuotekuva" />\n\
                </a>\n\
            </div>\n\
            <div class="item-field">{2}</div>\n\
            <div class="item-price">{3} €/kpl</div>\n\
            {4}', 
            self.large_image,  
            self.small_image, 
            num_field, 
            self.price, 
            available_html
        )
    
class StoreProductsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StoreProductsForm, self).__init__(*args, **kwargs)

        for item in StoreItem.items_available():
            name = 'item-%s' % item.id
            self.fields[name] = forms.IntegerField(
                widget=ProductWidget(attrs={
                    'small_image': item.imagefile_thumbnail.url,
                    'large_image': item.imagefile_original.url,
                    'available': item.num_in_store(),
                    'price': item.price,
                }),
                initial=0, 
                min_value=0, 
                max_value=item.num_available(),
                label=u'%s' % (item.name),
                help_text=item.description, 
                required=False
            )
            
    def _dataitems(self):
        for key, value in self.data.iteritems():
            try:
                pos = key.rfind('item-') + 5
                if pos > -1 and int(value):
                    yield (key[pos:], int(value))
            except:
                continue

    def clean(self):
        cleaned_data = super(StoreProductsForm, self).clean()
        total_items = 0
        fails = []

        # also check that the purchase amount for each field makes sense
        for item_id, amount in self._dataitems():
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
        label=u'Vahvista sähköposti', 
        max_length=255
    )

    def __init__(self, *args, **kwargs):
        super(StoreInfoForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(StoreInfoForm, self).clean()
        fails = []

        # Make sure the email fields match
        if cleaned_data['email'] != cleaned_data['email_confirm']:
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
        fields = ('firstname', 'lastname', 'email', 'telephone', 'mobile', 'company', 'street', 'postalcode', 'city', 'country', 'information')
        
class StorePaymentMethodForm(forms.Form):
    read_terms = forms.BooleanField(
        label=u'Hyväksyn toimitusehdot', 
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(StorePaymentMethodForm, self).__init__(*args, **kwargs)
        
        self.fields['read_terms'].help_text = \
            u'Olen lukenut <a href="%s" target="_blank">toimitusehdot</a> ' \
            u'ja hyväksyn ne. (Luethan myös <a href="%s" target="_blank">rekisteriselosteen</a>)' % (reverse('store:terms'), reverse('store:privacy'))

