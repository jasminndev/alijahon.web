from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from root.settings import MEDIA_ROOT, MEDIA_URL

urlpatterns = [path('i18n/', include('django.conf.urls.i18n')),] + static(MEDIA_URL, document_root=MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('apps.urls'))
)
