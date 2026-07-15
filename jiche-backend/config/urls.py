from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.shops.urls')),
    path('api/', include('apps.catalog.urls')),
    path('api/', include('apps.bikes.urls')),
    path('api/', include('apps.messaging.urls')),
    path('api/', include('apps.favorites.urls')),
]

# Docker/生产下也允许 gunicorn 直接提供 media（nginx 优先静态挂载；此为兜底）
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
