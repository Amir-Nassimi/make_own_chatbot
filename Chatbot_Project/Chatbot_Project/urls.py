from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

from rest_framework import permissions

from drf_yasg import openapi
from drf_yasg.views import get_schema_view


schema_view = get_schema_view(
   openapi.Info(
      title="Chatbot Project",
      default_version='v1',
      description="This app is designed to manage the requests on clients",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="nassimiamir@gmail.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Auth.urls')),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
