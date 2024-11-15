from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet


router = DefaultRouter()
router.register(r'', AuthViewSet, basename='auth')

urlpatterns = router.urls