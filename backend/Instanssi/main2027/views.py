from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def page_loader(request: HttpRequest, template_name: str) -> HttpResponse:
    # Instanssi ID is 27 in production database, so we hardcode that.
    return render(request, f"main2027/{template_name}.html", {"event_id": 27, "templatename": template_name})
