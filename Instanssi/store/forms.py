# -*- coding: utf-8 -*-
# Forms for the Instanssi store.

from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import \
    Submit, Layout, Fieldset, ButtonHolder, Hidden, Div, HTML
from Instanssi.store.models import StoreItem, TransactionItem, StoreTransaction


class StoreOrderForm(forms.ModelForm):
    """Displays an order form with items for a specific event listed."""

    email_confirm = forms.EmailField(
        label=u'Vahvista sähköposti', max_length=255
    )

    read_terms = forms.BooleanField(
        label=u'Hyväksyn käyttöehdot', required=True
    )

    def __init__(self, *args, **kwargs):
        self.event_id = kwargs.pop('event_id', None)
        super(StoreOrderForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'store'

        self.fields['read_terms'].help_text = \
            u'Olen lukenut <a href="%s" target="_blank">käyttöehdot</a> ' \
            u'ja hyväksyn ne.' % reverse('store:terms')

        item_fields = Fieldset(u'Saatavilla', css_class='store-items')
        for item in StoreItem.items_for_event(self.event_id):
            name = 'item-%s' % item.id
            self.fields[name] = forms.IntegerField(
                initial=0, min_value=0, max_value=item.num_available(),
                label=u'%s' % (item.name),
                help_text=item.description, required=False
            )

            item_fields.fields.append(
                Div(
                    HTML(u'<span class="item-price">%.2f €/kpl</span>'
                         % item.price),
                    name,
                )
            )

        self.helper.layout = Layout(
            item_fields,
            Fieldset(
                u'Maksajan tiedot',
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

        if commit:
            new_transaction.save()

        transaction_items = []

        for (item_id, amount) in self._dataitems():
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
        exclude = ('time_created', 'time_paid', 'token', 'paid', 'key')
