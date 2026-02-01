from typing import Any, Optional

import orjson
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Field
from django.utils.translation import gettext_lazy as _

from Instanssi.common.youtube.forms import YoutubeFormField
from Instanssi.common.youtube.parser import InvalidYoutubeUrlError, YoutubeURL


class YoutubeVideoField(models.JSONField):
    description = _("Youtube URL")
    default_error_messages = {"invalid": _("Value is not a youtube URL")}
    _default_hint = ("dict", "{}")

    def from_db_value(self, value, expression, connection) -> Optional[YoutubeURL]:
        value = super().from_db_value(value, expression, connection)
        if not value:
            return None
        # Handle legacy data where start might be stored as a string
        start = value.get("start")
        start = int(start) if start else None
        return YoutubeURL(video_id=value["video_id"], start=start)

    def to_python(self, value: Any) -> Optional[YoutubeURL]:
        if not value:
            return None
        if isinstance(value, YoutubeURL):
            return value
        if isinstance(value, dict):
            return YoutubeURL(video_id=value["video_id"], start=value.get("start"))
        return YoutubeURL.from_url(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return orjson.dumps(dict(video_id=value.video_id, start=value.start)).decode()

    def validate(self, value, model_instance):
        if value is None:
            return
        if isinstance(value, YoutubeURL):
            return
        if isinstance(value, str):
            try:
                YoutubeURL.from_url(value)
            except InvalidYoutubeUrlError as e:
                raise ValidationError(self.default_error_messages["invalid"]) from e

    def get_prep_value(self, value: Optional[YoutubeURL]) -> Optional[str]:
        if not value:
            return None
        if isinstance(value, str):
            value = YoutubeURL.from_url(value)
        return super().get_prep_value(dict(video_id=value.video_id, start=value.start))

    def formfield(self, **kwargs):
        return Field.formfield(
            self,
            **{
                "form_class": YoutubeFormField,
                **kwargs,
            },
        )
