from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/", include("users.urls")),
    path("api/classroom/", include("classrooms.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/forum/", include("forum.urls")),
    path("api/learning-path/", include("learning_path_generator.urls")),
    # path("api/", include("assessments.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

