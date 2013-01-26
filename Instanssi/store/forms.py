# Forms for the Instanssi store.

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Hidden
from Instanssi.store.models import StoreItem, TransactionItem, StoreTransaction


class StoreOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        event_id = kwargs.pop('event_id', None)
        super(StoreOrderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        item_fields = Fieldset(u'Saatavilla')
        for item in StoreItem.items_for_event(event_id):
            name = "item-%s" % item.id
            self.fields[name] = forms.IntegerField()
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

    class Meta:
        model = StoreTransaction
        exclude = ('time', 'token', 'paid')  # filled in later
