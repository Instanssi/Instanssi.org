from django import template
from tabulate import tabulate

register = template.Library()


@register.simple_tag
def render_product_list(products):
    return tabulate(
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


@register.filter
def absolute_url(path, request):
    return request.build_absolute_uri(path)
