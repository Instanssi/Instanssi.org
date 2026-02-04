from typing import Any

from django.core.exceptions import ValidationError
from django.forms import fields
from django.utils.translation import gettext_lazy as _

from Instanssi.common.youtube.parser import InvalidYoutubeUrlError, YoutubeURL


class YoutubeFormField(fields.CharField):
    def to_python(self, value: Any) -> YoutubeURL | None:  # type: ignore[override]
        if not value:
            return None
        str_value = super().to_python(value)
        if not str_value:
            return None
        try:
            return YoutubeURL.from_url(str_value)
        except InvalidYoutubeUrlError as e:
            raise ValidationError(_("%(value)s is not a youtube URL"), params={"value": value}) from e

    def prepare_value(self, value: Any) -> str:
        if isinstance(value, YoutubeURL):
            return value.link_url
        return str(value) if value else ""
