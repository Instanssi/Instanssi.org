from django.urls import path

from Instanssi.ext_blog.views import BlogFeed

app_name = "ext_blog"


urlpatterns = [
    path("rss/", BlogFeed(), name="rss"),
]
