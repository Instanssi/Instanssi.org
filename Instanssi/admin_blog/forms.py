from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms

from Instanssi.ext_blog.models import BlogEntry


class BlogEntryEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlogEntryEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Muokkaa blogientryä",
                "title",
                "text",
                "date",
                "public",
                ButtonHolder(Submit("submit", "Tallenna")),
            )
        )

    class Meta:
        model = BlogEntry
        fields = ("title", "text", "public", "date")


class BlogEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlogEntryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Lisää uusi blogientry",
                "title",
                "text",
                "public",
                ButtonHolder(Submit("submit", "Tallenna")),
            )
        )

    class Meta:
        model = BlogEntry
        fields = ("title", "text", "public")
