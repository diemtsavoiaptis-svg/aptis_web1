from core import views as core_views
from core import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("dashboard/part-3/", core_views.part3_admin_only, name="part3_admin_only"),
    path("part-3/", core_views.part3_student_only, name="part3_student_only"),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
