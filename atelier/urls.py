from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Content Studio"
admin.site.site_title = "Content Studio"
admin.site.index_title = "Every word and every image lives here"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("sitecontent.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
