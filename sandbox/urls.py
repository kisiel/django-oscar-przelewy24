from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static

from apps.app import shop

import debug_toolbar

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^__debug__/', include(debug_toolbar.urls)),

    url(r'^przelewy24/', include('przelewy24.urls')),
    url(r'', include(shop.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    # The Django admin is not officially supported; expect breakage.
    # Nonetheless, it's often useful for debugging.
    urlpatterns += url(r'^admin/', include(admin.site.urls)),