from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def page_loader(request: HttpRequest, template_name: str) -> HttpResponse:
    return render(
        request, "main2022/" + template_name + ".html", {"event_id": 21, "templatename": template_name}
    )
