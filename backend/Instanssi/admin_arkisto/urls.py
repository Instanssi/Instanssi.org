from django.urls import path

from Instanssi.admin_arkisto.views import (
    archiver,
    delete_video,
    delete_video_category,
    edit_video,
    edit_video_category,
    hide,
    index,
    optimizes_scores,
    remove_old_votes,
    show,
    transfer_rights,
    video_categories,
    videos,
)

app_name = "admin_arkisto"


urlpatterns = [
    path("", index, name="index"),
    path("archiver/", archiver, name="archiver"),
    path("show/", show, name="archiver-show"),
    path("hide/", hide, name="archiver-hide"),
    path("transferrights/", transfer_rights, name="archiver-tr"),
    path("optimizescores/", optimizes_scores, name="archiver-os"),
    path("removeoldvotes/", remove_old_votes, name="archiver-rv"),
    path("vids/", videos, name="vids"),
    path("vidcats/", video_categories, name="vidcats"),
    path("deletevid/<int:video_id>/", delete_video, name="vids-delete"),
    path("deletecat/<int:category_id>/", delete_video_category, name="vidcats-delete"),
    path("editvid/<int:video_id>/", edit_video, name="vids-edit"),
    path("editcat/<int:category_id>/", edit_video_category, name="vidcats-edit"),
]
