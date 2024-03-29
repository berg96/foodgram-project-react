from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from .views import (
    IngredientViewSet, RecipeViewSet, TagViewSet, UserWithSubscriptionViewSet
)

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('users', UserWithSubscriptionViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    url('auth/', include('djoser.urls.authtoken')),
    url('', include(router.urls)),
]
