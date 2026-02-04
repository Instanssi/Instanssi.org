from typing import Any

import nh3
from django.db.models import TextField


class SanitizedHtmlField(TextField):  # type: ignore[type-arg]
    def to_python(self, value: Any) -> str | None:
        result: str | None = super().to_python(value)
        if result:
            result = nh3.clean(result)
        return result
