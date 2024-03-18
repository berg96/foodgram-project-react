from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from .views import IngredientViewSet, TagViewSet, CustomUserViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    url('auth/', include('djoser.urls.authtoken')),
    url('', include(router_v1.urls)),
]
