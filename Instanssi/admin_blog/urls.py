from django.conf.urls import url
from Instanssi.admin_blog.views import index, delete, edit

app_name = "admin_blog"


urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^delete/(?P<entry_id>\d+)/', delete, name="delete"),
    url(r'^edit/(?P<entry_id>\d+)/', edit, name="edit"),
]
