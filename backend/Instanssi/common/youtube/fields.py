from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Field
from django.forms import ChoiceField
from django.forms import Field as FormField
from django.utils.translation import gettext_lazy as _

from Instanssi.common.youtube.forms import YoutubeFormField
from Instanssi.common.youtube.parser import InvalidYoutubeUrlError, YoutubeURL


class YoutubeVideoField(models.JSONField):
    description = _("Youtube URL")
    default_error_messages = {"invalid": _("Value is not a youtube URL")}
    _default_hint = ("dict", "{}")

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> YoutubeURL | None:
        value = super().from_db_value(value, expression, connection)
        if not value:
            return None
        # Handle legacy data where start might be stored as a string
        start = value.get("start")
        start = int(start) if start else None
        return YoutubeURL(video_id=value["video_id"], start=start)

    def to_python(self, value: Any) -> YoutubeURL | None:
        if not value:
            return None
        if isinstance(value, YoutubeURL):
            return value
        if isinstance(value, dict):
            return YoutubeURL(video_id=value["video_id"], start=value.get("start"))
        return YoutubeURL.from_url(value)

    def value_to_string(self, obj: Any) -> str:
        value = self.value_from_object(obj)
        if not value:
            return ""
        return str(value)

    def validate(self, value: Any, model_instance: Any) -> None:
        if value is None:
            return
        if isinstance(value, YoutubeURL):
            return
        if isinstance(value, str):
            try:
                YoutubeURL.from_url(value)
            except InvalidYoutubeUrlError as e:
                raise ValidationError(self.default_error_messages["invalid"]) from e

    def get_prep_value(self, value: YoutubeURL | None) -> str | None:
        if not value:
            return None
        if isinstance(value, str):
            value = YoutubeURL.from_url(value)
        result: str | None = super().get_prep_value(dict(video_id=value.video_id, start=value.start))
        return result

    def formfield(
        self,
        form_class: type[FormField] | None = None,
        choices_form_class: type[ChoiceField] | None = None,
        **kwargs: Any,
    ) -> FormField | None:
        return Field.formfield(
            self,
            form_class=form_class or YoutubeFormField,
            choices_form_class=choices_form_class,
            **kwargs,
        )
