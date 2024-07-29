from django.urls import path
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from .views import UsersViewSet


schema_view = get_schema_view(
   openapi.Info(
      title="Chatbot Project - Client APIS",
      default_version='v1',
      description="This app is designed to manage the requests on clients",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="nassimiamir@gmail.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


router = DefaultRouter()
router.register(r'', UsersViewSet, basename='user')

urlpatterns = router.urls
urlpatterns += [
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]
