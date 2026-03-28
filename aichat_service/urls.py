from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RecommendationViewSet, ChatViewSet

# 创建路由
router = DefaultRouter()
router.register(r'recommend', RecommendationViewSet, basename='recommend')
router.register(r'chat', ChatViewSet, basename='chat')

urlpatterns = router.urls
