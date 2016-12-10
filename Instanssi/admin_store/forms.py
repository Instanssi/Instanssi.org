# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, HTML, Div
from Instanssi.store.models import StoreItem, StoreItemVariant
from Instanssi.kompomaatti.models import Event


class StoreItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StoreItemForm, self).__init__(*args, **kwargs)
        self.fields['event'].required = True
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'event',
            'name',
            'description',
            'price',
            'max',
            'available',
            'max_per_order',
            'imagefile_original',
            'sort_index',
            'discount_amount',
            'discount_percentage',
            Div(HTML('Tuotteen alityypit alla. Täytä kentät jotka tarvitset. Mikäli kentät loppuvat kesken, '
                     'tallenna välillä ja muokkaa.'), css_class="ctrlHolder")
        )

    class Meta:
        model = StoreItem
        exclude = ('imagefile_thumbnail',)


class StoreItemVariantForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StoreItemVariantForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(Div(Fieldset('Alityyppi', 'name'), css_class="inner_form"))

    class Meta:
        model = StoreItemVariant
        fields = ('name',)


class TaItemExportForm(forms.Form):
    def get_event_list(self):
        out = []
        for ev in Event.objects.all().order_by('-id'):
            out.append((ev.id, ev.name))
        return out
    
    def __init__(self, *args, **kwargs):
        super(TaItemExportForm, self).__init__(*args, **kwargs)
        self.fields['event'] = forms.ChoiceField(choices=self.get_event_list())
        self.fields['event'].required = True
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Vie',
                'event',
                ButtonHolder(
                    Submit('submit', 'Vie')
                )
            )
        )
