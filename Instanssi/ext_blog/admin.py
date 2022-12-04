from django.contrib import admin

from Instanssi.ext_blog.models import BlogComment, BlogEntry

admin.site.register(BlogEntry)
admin.site.register(BlogComment)
