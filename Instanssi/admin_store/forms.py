# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.store.models import StoreItem
from Instanssi.kompomaatti.models import Event


class StoreItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StoreItemForm, self).__init__(*args, **kwargs)
        self.fields['event'].required = True
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Tuote',
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
                ButtonHolder(
                    Submit('submit', u'Tallenna')
                )
            )
        )

    class Meta:
        model = StoreItem
        exclude = ('imagefile_thumbnail',)


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
                u'Vie',
                'event',
                ButtonHolder(
                    Submit('submit', u'Vie')
                )
            )
        )
