# Forms for the Instanssi store.

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Hidden

from Instanssi.store.models import TransactionItem, StoreTransaction


class StoreTransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StoreTransactionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
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
