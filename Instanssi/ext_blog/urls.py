from django.urls import path

from Instanssi.ext_blog.views import BlogFeed, BlogFeedAll

app_name = "ext_blog"


urlpatterns = [
    path("<int:event_id>/rss/", BlogFeed(), name="rss_single"),
    path("rss/", BlogFeedAll(), name="rss"),
]
