from rest_framework.routers import DefaultRouter


from .views import TrainableDataViewSet, ChatBotViewSet



router = DefaultRouter()
router.register(r'train', TrainableDataViewSet)
router.register(r'', ChatBotViewSet, basename='chatbot')

urlpatterns = router.urls
