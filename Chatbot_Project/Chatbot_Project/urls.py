from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

from rest_framework import permissions


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Auth.urls')),
    path('user/', include('Clients.urls')),
    path('chatbot/', include('Service_Provider.urls'))
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
