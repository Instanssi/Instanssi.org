# -*- coding: utf-8 -*-
# Forms for the Instanssi store.

from datetime import datetime
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Hidden
from Instanssi.store.models import StoreItem, TransactionItem, StoreTransaction


class StoreOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.event_id = kwargs.pop('event_id', None)
        super(StoreOrderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        item_fields = Fieldset(u'Saatavilla')
        for item in StoreItem.items_for_event(self.event_id):
            name = "item-%s" % item.id
            self.fields[name] = forms.IntegerField(
                min_value=0, max_value=item.num_available()
            )
            self.fields[name].label = item.name
            self.fields[name].help_text = item.description
            self.fields[name].initial = 0
            item_fields.fields.append(name)

        self.helper.layout = Layout(
            item_fields,
            Fieldset(
                u'Maksajan tiedot',
                'firstname',
                'lastname',
                'email',
                'telephone',
                'mobile',
                'company',
                'street',
                'postalcode',
                'city',
                'country',
                ButtonHolder(
                    Submit('Buy', u'Osta')
                )
            )
        )

    def _dataitems(self):
        item_keys = filter(
            lambda k: k.startswith('item-'),
            [x for x in self.data]
        )
        return [(k[5:], int(self.data[k][0])) for k in item_keys]

    def clean(self):
        cleaned_data = super(StoreOrderForm, self).clean()

        # also check that the purchase amount for each field makes sense
        for (item_id, amount) in self._dataitems():
            store_item = StoreItem.objects.get(id=int(item_id))
            if store_item.num_available() < amount:
                raise forms.ValidationError(
                    u"Esinettä '%s' ei ole saatavilla riittävästi!"
                    % store_item.name
                )
        return cleaned_data

    def save(self, commit=True):
        """Saves a store transaction form, also generating TransactionItems
        for each item in the post data."""

        new_transaction = super(StoreOrderForm, self).save(commit=False)
        new_transaction.time = datetime.now()

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
        exclude = ('time', 'token', 'paid')  # filled in later
