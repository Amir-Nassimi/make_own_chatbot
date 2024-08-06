from rest_framework.routers import DefaultRouter


from .views import TrainableDataViewSet, ChatBotViewSet, ProvideServiceViewSet



router = DefaultRouter()
router.register(r'train', TrainableDataViewSet)
router.register(r'', ChatBotViewSet, basename='chatbot')
router.register(r'init', ProvideServiceViewSet, basename='service')

urlpatterns = router.urls
