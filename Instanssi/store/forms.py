# -*- coding: utf-8 -*-
# Forms for the Instanssi store.

import time
import random
from datetime import datetime

from django import forms
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from Instanssi.store.models import StoreTransaction, TransactionItem, StoreItem
from Instanssi.store.utils.hash import gen_sha

# Logger
import logging
logger = logging.getLogger(__name__)


class StoreProductsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StoreProductsForm, self).__init__(*args, **kwargs)

        # generate quantity field for each item and provide it with item data
        for item in StoreItem.items_available():
            name = 'item-%s' % item.id
            field = forms.IntegerField(
                initial='0',
                label=u'{}'.format(item.name),
                help_text=item.description,
                required=False,
                widget=forms.TextInput()
            )
            self.fields[name] = field
            attribs = field.widget.attrs
            attribs['data-price'] = item.price
            attribs['data-min'] = 0
            attribs['data-max'] = item.num_available()
            attribs['data-discount-amount'] = item.discount_amount
            attribs['data-discount-factor'] = item.get_discount_factor()
            attribs['class'] = 'item-amount-field'
            field.image_large = item.imagefile_original.url \
                if item.imagefile_original else None
            field.image_small = item.imagefile_thumbnail.url \
                if item.imagefile_thumbnail else None
            field.available = item.num_in_store()
            field.price = item.price
            field.has_discount = item.is_discount_available()
            field.discount_amount = item.discount_amount
            field.discount_percentage = item.discount_percentage

    def _dataitems(self):
        for key, value in self.data.iteritems():
            try:
                pos = key.rfind('item-')
                if pos > -1 and int(value):
                    yield (key[pos + 5:], int(value))
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

    def save(self, transaction):
        for (item_id, amount) in self._dataitems():
            if not amount > 0:
                continue
            store_item = StoreItem.objects.get(id=item_id)

            discounted_price = store_item.get_discounted_unit_price(amount)

            for i in range(amount):
                new_item = TransactionItem()
                new_item.item = store_item
                new_item.transaction = transaction

                for i in range(10):
                    try:
                        str = u'%s|%s|%s|%s' % (
                            i, store_item.name, time.time(),
                            random.random())
                        new_item.key = gen_sha(str.encode('utf-8'))
                        new_item.purchase_price = discounted_price
                        new_item.original_price = store_item.price
                        new_item.save()
                        break
                    except IntegrityError as ex:
                        logger.warning("SHA-1 Collision in item. Key: %s, exception: %s." % (new_item.key, ex))


class StoreInfoForm(forms.ModelForm):
    email_confirm = forms.EmailField(
        label=u'Vahvista sähköposti',
        max_length=255,
        required=True,
        help_text=u'Varmista sähköposti kirjoittamalla se vielä uudelleen.'
    )

    def __init__(self, *args, **kwargs):
        super(StoreInfoForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
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
            'information'
        ]

    def clean(self):
        cleaned_data = super(StoreInfoForm, self).clean()
        fails = []

        # Make sure the email fields match
        if 'email' in cleaned_data and 'email_confirm' in cleaned_data:
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

    def save(self, commit=True):
        """Saves the form content to a new transaction"""

        new_transaction = super(StoreInfoForm, self).save(commit=False)
        new_transaction.time_created = datetime.now()

        for i in range(10):
            try:
                str = u'%s|%s|%s|%s|%s' % (i, new_transaction.firstname, new_transaction.lastname,
                                           time.time(), random.random())
                new_transaction.key = gen_sha(str.encode('utf-8'))
                new_transaction.save()
                break
            except IntegrityError as ex:
                logger.warning("SHA-1 Collision in transaction. Key: %s, exception: %s." % (new_transaction.key, ex))

        return new_transaction

    class Meta:
        model = StoreTransaction
        fields = (
            'firstname', 'lastname', 'email', 'telephone', 'mobile',
            'company', 'street', 'postalcode', 'city', 'country', 'information'
        )


class StorePaymentMethodForm(forms.Form):
    payment_method = forms.ChoiceField(
        label=u'Maksutapa',
        required=True,
        choices=[(0, u'Bitcoin'), (1, u'Verkkomaksu')],
        widget=forms.RadioSelect(),
    )
    read_terms = forms.BooleanField(
        label=u'Hyväksyn toimitusehdot',
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(StorePaymentMethodForm, self).__init__(*args, **kwargs)

        self.fields['payment_method'].help_text = \
            u'Valitse mieleisesi maksutapa. Verkkomaksu-valinta kattaa sekä verkkopankki- että luottokorttimaksut.'
        self.fields['read_terms'].help_text = \
            u'Olen lukenut <a href="%s" target="_blank">toimitusehdot</a> ja hyväksyn ne. ' \
            u'(Luethan myös <a href="%s" target="_blank">rekisteriselosteen</a>)' \
            % (reverse('store:terms'), reverse('store:privacy'))
