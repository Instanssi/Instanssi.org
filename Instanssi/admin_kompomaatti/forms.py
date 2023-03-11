from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from Instanssi.common.misc import parse_youtube_video_id
from Instanssi.kompomaatti.models import (
    Competition,
    CompetitionParticipation,
    Compo,
    Entry,
    Event,
)


class AdminCompetitionScoreForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.competition = kwargs.pop("competition", None)

        # Init
        super(AdminCompetitionScoreForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout()

        # Create a fieldset for everything
        fs = Fieldset("Pisteytys")

        # Set fields
        participants = CompetitionParticipation.objects.filter(competition=self.competition)
        for p in participants:
            name = str(p.id)
            self.fields[name] = forms.FloatField()
            self.fields[name].label = p.participant_name
            self.fields[name].help_text = "Osallistujan {} saavuttama tulos.".format(p.participant_name)
            self.fields[name].initial = p.score
            fs.fields.append(name)

        # Add buttonholder
        bh = ButtonHolder(Submit("submit", "Tallenna"))
        fs.fields.append(bh)

        # Add fieldset to layout
        self.helper.layout.fields.append(fs)

    def save(self):
        for k, v in self.cleaned_data.items():
            p = get_object_or_404(CompetitionParticipation, pk=int(k))
            p.score = v
            p.save()


class AdminParticipationEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminParticipationEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Osallistuja",
                "participant_name",
                "score",
                "disqualified",
                "disqualified_reason",
                ButtonHolder(Submit("submit", "Tallenna")),
            )
        )

    class Meta:
        model = CompetitionParticipation
        fields = ("participant_name", "score", "disqualified", "disqualified_reason")


class AdminCompetitionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminCompetitionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Kilpailu",
                "name",
                "description",
                "participation_end",
                "start",
                "end",
                "score_type",
                "score_sort",
                "show_results",
                "hide_from_archive",
                "active",
                ButtonHolder(Submit("submit", "Tallenna")),
            )
        )

    class Meta:
        model = Competition
        exclude = ("event",)


class AdminCompoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminCompoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Kompo",
                "name",
                "description",
                "adding_end",
                "editing_end",
                "compo_start",
                "voting_start",
                "voting_end",
                "entry_sizelimit",
                "source_sizelimit",
                "formats",
                "source_formats",
                "image_formats",
                "thumbnail_pref",
                "active",
                "show_voting_results",
                "entry_view_type",
                "hide_from_archive",
                "hide_from_frontpage",
                "is_votable",
                ButtonHolder(Submit("submit-compo", "Tallenna")),
            )
        )

    def clean_formats(self):
        return self.cleaned_data["formats"].lower()

    def clean_image_formats(self):
        return self.cleaned_data["image_formats"].lower()

    def clean_source_formats(self):
        return self.cleaned_data["source_formats"].lower()

    def clean(self):
        data = super().clean()

        # Make sure that automatic thumbnails from entry field is only acceptable if field only accepts image files.
        formats = data["formats"].split("|")
        is_image = all([f in ["png", "jpg", "jpeg"] for f in formats])
        if data["thumbnail_pref"] == 1 and not is_image:
            raise ValidationError(
                "Automaattiset thumbnailit käytettävissä vain jos "
                "sallitut tiedostoformaatit ovat kuvaformaatteja (png, jpg)"
            )

        return data

    class Meta:
        model = Compo
        exclude = ("event",)


class AdminEntryAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Initialize
        self.event = kwargs.pop("event", None)
        super(AdminEntryAddForm, self).__init__(*args, **kwargs)

        # Set choices
        if self.event:
            compos = []
            for compo in Compo.objects.filter(event=self.event):
                compos.append((compo.id, compo.name))
            self.fields["compo"].choices = compos

        # Set form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Tuotos",
                "user",
                "compo",
                "name",
                "description",
                "creator",
                "platform",
                "entryfile",
                "sourcefile",
                "imagefile_original",
                "youtube_url",
                ButtonHolder(Submit("submit", "Lisää")),
            )
        )

    def clean_youtube_url(self):
        # Make sure field has content
        if not self.cleaned_data["youtube_url"]:
            return self.cleaned_data["youtube_url"]

        # Parse video id
        video_id = parse_youtube_video_id(self.cleaned_data["youtube_url"])

        # Warn if something is wrong
        if not video_id:
            raise ValidationError("Osoitteesta ei löytynyt videotunnusta.")

        # Return a new video url
        return "https://www.youtube.com/v/{}".format(video_id)

    class Meta:
        model = Entry
        exclude = (
            "created_at",
            "disqualified",
            "disqualified_reason",
            "imagefile_thumbnail",
            "imagefile_medium",
            "archive_score",
            "archive_rank",
        )


class AdminEntryEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Initialize
        self.event = kwargs.pop("event", None)
        super(AdminEntryEditForm, self).__init__(*args, **kwargs)

        # Set choices for Compo field
        if self.event:
            compos = []
            for compo in Compo.objects.filter(event=self.event):
                compos.append((compo.id, compo.name))
            self.fields["compo"].choices = compos

        # Make entryfile not required for editform
        self.fields["entryfile"].required = False

        # Set form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Tuotos",
                "compo",
                "user",
                "name",
                "description",
                "creator",
                "platform",
                "entryfile",
                "sourcefile",
                "imagefile_original",
                "youtube_url",
                "disqualified",
                "disqualified_reason",
                ButtonHolder(Submit("submit", "Tallenna")),
            )
        )

    def clean_youtube_url(self):
        # Make sure field has content
        if not self.cleaned_data["youtube_url"]:
            return self.cleaned_data["youtube_url"]

        # Parse video id
        video_id = parse_youtube_video_id(self.cleaned_data["youtube_url"])

        # Warn if something is wrong
        if not video_id:
            raise ValidationError("Osoitteesta ei löytynyt videotunnusta.")

        # Return a new video url
        return "https://www.youtube.com/v/{}".format(video_id)

    class Meta:
        model = Entry
        exclude = ("created_at", "imagefile_thumbnail", "imagefile_medium", "archive_score", "archive_rank")


class CloneCompoForm(forms.Form):
    event = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(CloneCompoForm, self).__init__(*args, **kwargs)
        self.fields["event"].choices = [(event.pk, event.name) for event in Event.objects.all().iterator()]
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Kloonaa toisen tapahtuman kompot",
                "event",
                ButtonHolder(Submit("submit-clone", "Kloonaa")),
            )
        )

    def save(self, event_id, commit=False):
        for compo in Compo.objects.filter(event=self.cleaned_data["event"]).iterator():
            compo.pk = None
            compo.event = Event.objects.get(pk=event_id)
            compo.active = False
            compo.hide_from_archive = True
            compo.hide_from_frontpage = True
            compo.is_votable = False
            compo.save()
