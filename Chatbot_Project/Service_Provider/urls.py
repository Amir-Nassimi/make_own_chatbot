from rest_framework.routers import DefaultRouter


from .views import TrainableDataViewSet



router = DefaultRouter()
router.register(r'train', TrainableDataViewSet)

urlpatterns = router.urls
