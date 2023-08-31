from django.urls import path

from Instanssi.main2024.views import page_loader

app_name = "main2024"

urlpatterns = [
    path("", page_loader, {"template_name": "index"}, name="index"),
    path("info/", page_loader, {"template_name": "info"}, name="info"),
    path("english/", page_loader, {"template_name": "english"}, name="english"),
    path("ohjelma/", page_loader, {"template_name": "ohjelma"}, name="ohjelma"),
    path("aikataulu/", page_loader, {"template_name": "aikataulu"}, name="aikataulu"),
    path("kompot/", page_loader, {"template_name": "kompot"}, name="kompot"),
    path("kilpailusopimus/", page_loader, {"template_name": "kilpailusopimus"}, name="kilpailusopimus"),
    path("stream/", page_loader, {"template_name": "stream"}, name="stream"),
    path("saannot/", page_loader, {"template_name": "saannot"}, name="saannot"),
    path("valot/", page_loader, {"template_name": "valot"}, name="valot"),
    path("radio/", page_loader, {"template_name": "radio"}, name="radio"),
]
