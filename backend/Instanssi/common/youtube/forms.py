from typing import Optional

from django.core.exceptions import ValidationError
from django.forms import fields
from django.utils.translation import gettext_lazy as _

from Instanssi.common.youtube.parser import InvalidYoutubeUrlError, YoutubeURL


class YoutubeFormField(fields.CharField):
    def to_python(self, value: str) -> Optional[YoutubeURL]:
        if not value:
            return None
        try:
            return YoutubeURL.from_url(super().to_python(value))
        except InvalidYoutubeUrlError as e:
            raise ValidationError(_("%(value)s is not a youtube URL"), params={"value": value}) from e

    def prepare_value(self, value) -> str:
        if isinstance(value, YoutubeURL):
            return value.link_url
        return value
