from typing import Any

from django import template
from django.http import HttpRequest
from tabulate import tabulate

register = template.Library()


@register.simple_tag
def render_product_list(products: list[dict[str, Any]]) -> str:
    return str(
        tabulate(
            tabular_data=products,
            tablefmt="simple",
            headers={
                "id": "ID",
                "name": "Tuoteseloste",
                "price": "Hinta (€)",
                "amount": "Määrä",
                "total": "Yhteensä (€)",
                "tax": "Alv.",
            },
        )
    )


@register.filter
def absolute_url(path: str, request: HttpRequest) -> str:
    return request.build_absolute_uri(path)
