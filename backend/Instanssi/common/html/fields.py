from typing import Any

import nh3
from django.db.models import TextField


class SanitizedHtmlField(TextField):
    def to_python(self, value: Any) -> str | None:
        if value := super().to_python(value):
            value = nh3.clean(value)
        return value
