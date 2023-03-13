from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms

from Instanssi.arkisto.models import OtherVideo, OtherVideoCategory


class VideoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Initialize
        self.event = kwargs.pop("event", None)
        super(VideoForm, self).__init__(*args, **kwargs)

        # Set choices
        if self.event:
            cats = []
            for cat in OtherVideoCategory.objects.filter(event=self.event):
                cats.append((cat.id, cat.name))
            self.fields["category"].choices = cats

        # Set form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Muu Video",
                "name",
                "category",
                "description",
                "youtube_url",
                ButtonHolder(Submit("submit", "Tallenna")),
            )
        )

    class Meta:
        model = OtherVideo
        fields = ("category", "name", "description", "youtube_url")


class VideoCategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VideoCategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset("Kategoria", "name", ButtonHolder(Submit("submit", "Tallenna")))
        )

    class Meta:
        model = OtherVideoCategory
        fields = ("name",)
