from django.urls import path

from Instanssi.admin_slides.views import index, slide_entries, slide_results

app_name = "admin_slides"


urlpatterns = [
    path("", index, name="index"),
    path("slide_entries/<int:compo_id>/", slide_entries, name="entries"),
    path("slide_results/<int:compo_id>/", slide_results, name="results"),
]
