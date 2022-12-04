from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.kompomaatti.models import Profile
from Instanssi.common.misc import get_url_local_path


class DjangoLoginForm(forms.Form):
    username = forms.CharField(label="Käyttäjätunnus", help_text="Django-käyttäjätunnus")
    password = forms.CharField(label="Salasana", widget=forms.PasswordInput)
    next = forms.CharField(widget=forms.HiddenInput)
    
    def __init__(self, *args, **kwargs):
        self.next_page = kwargs.pop('next', '')
        self.logged_user = None
        super(DjangoLoginForm, self).__init__(*args, **kwargs)
        self.fields['next'].initial = self.next_page
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Django kirjautuminen',
                'username',
                'password',
                'next',
                ButtonHolder (
                    Submit('submit', 'Kirjaudu')
                )
            )
        )

    def clean_next(self):
        return get_url_local_path(self.cleaned_data['next'])

    def clean(self):
        # Make sure the user is valid
        cleaned_data = super(DjangoLoginForm, self).clean()
        
        if 'username' in self.cleaned_data and 'password' in self.cleaned_data:
            self.logged_user = auth.authenticate(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'])
            if not self.logged_user or self.logged_user.is_active is False:
                self.logged_user = None
                raise ValidationError('Väärä käyttäjätunnus tai salasana!')
        return cleaned_data

    def login(self, request):
        auth.login(request, self.logged_user)


class OpenIDLoginForm(forms.Form):
    sps = forms.ChoiceField(
        label='Kirjautumispalvelu', 
        help_text='Muutamia yleisimpiä kirjautumispalvelimia.')
    openid_identifier = forms.URLField(
        widget=forms.TextInput(), 
        max_length=255, 
        required=True, 
        label='Osoite', 
        help_text='Kirjautumispalvelun osoite. Voit joko valita ylläolevasta valikosta tunnetun, tai käyttää omaasi.')
    next = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        # Init
        self.next = kwargs.pop('next', "")
        super(OpenIDLoginForm, self).__init__(*args, **kwargs)
        
        # Build form
        self.helper = FormHelper()
        self.helper.form_action = reverse('social:begin', args=('openid',))
        self.helper.layout = Layout(
            Fieldset(
                'OpenID kirjautuminen',
                'sps',
                'openid_identifier',
                'next',
                ButtonHolder(
                    Submit('submit-login', 'Kirjaudu')
                )
            )
        )
        
        # Initial values
        self.fields['next'].initial = self.next
        self.fields['sps'].choices = [
            ('', 'Valitse OpenID-palveluntarjoaja'),
            ('https://korppi.jyu.fi/openid/', 'Korppi'),
            ('https://me.yahoo.com', 'Yahoo'),
        ]
        self.fields['sps'].required = False
        self.fields['sps'].initial = 0
        self.fields['openid_identifier'].initial = ''
        

class ProfileForm(forms.ModelForm):
    otherinfo = forms.CharField(
        widget=forms.Textarea(), 
        label="Muut yhteystiedot", 
        help_text="Muut yhteystiedot, mm. IRC-nick & verkko, jne.", 
        required=False)
    
    def __init__(self, *args, **kwargs):
        # Init
        self.user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        
        # Find profile
        try:
            self.profile = Profile.objects.get(user=self.user)
        except Profile.DoesNotExist:
            self.profile = Profile(user=self.user, otherinfo='')
            self.profile.save()
        
        # Build form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Käyttäjäprofiili',
                'first_name',
                'last_name',
                'email',
                'otherinfo',
                ButtonHolder (
                    Submit('submit-profile', 'Tallenna')
                )
            )
        )
        
        # Finnish labels
        self.fields['first_name'].label = "Etunimi"
        self.fields['last_name'].label = "Sukunimi"
        self.fields['email'].label = "Sähköposti"
        self.fields['email'].required = True
        self.fields['otherinfo'].initial = self.profile.otherinfo
                
    def save(self):
        super(ProfileForm, self).save()
        self.profile.otherinfo = self.cleaned_data['otherinfo']
        self.profile.save()
        
    class Meta:
        model = User
        fields = ('first_name','last_name','email')
