from pathlib import Path

from django.conf.urls.static import static
from django.urls import path

from Instanssi.management.views import management_index

app_name = "management"
CURRENT_DIR = Path(__file__).resolve(strict=True).parent

urlpatterns = [
    path("", management_index, name="index"),
] + static("/assets/", document_root=CURRENT_DIR / "site" / "assets")
