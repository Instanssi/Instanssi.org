from django.forms import ModelForm
from models import Entry

class AddEntryForm(ModelForm):
    class Meta:
        model = Entry