from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms
from django.core.exceptions import ValidationError

from Instanssi.store.models import StoreTransaction, TransactionItem


class ItemKeyScanForm(forms.Form):
    key = forms.CharField(label="Tunniste")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(ItemKeyScanForm, self).__init__(*args, **kwargs)
        self.item: TransactionItem | None = None
        self.helper = FormHelper()
        self.helper.layout = Layout(Fieldset("", "key", ButtonHolder(Submit("submit", "OK"))))

    def clean_key(self) -> str:
        key: str = self.cleaned_data["key"]
        try:
            self.item = TransactionItem.objects.get(key=key)
        except TransactionItem.DoesNotExist:
            raise ValidationError("Virheellinen tuoteavain!")
        return key


class TransactionKeyScanForm(forms.Form):
    key = forms.CharField(label="Tunniste")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(TransactionKeyScanForm, self).__init__(*args, **kwargs)
        self.transaction: StoreTransaction | None = None
        self.helper = FormHelper()
        self.helper.layout = Layout(Fieldset("", "key", ButtonHolder(Submit("submit", "OK"))))

    def clean_key(self) -> str:
        key: str = self.cleaned_data["key"]
        try:
            self.transaction = StoreTransaction.objects.get(key=key)
        except StoreTransaction.DoesNotExist:
            raise ValidationError("Virheellinen transaktioavain!")
        return key
