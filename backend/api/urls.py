from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import include
from rest_framework import routers

from .views import (
    CustomUserViewSet, IngredientViewSet, RecipeViewSet, TagViewSet
)

router_v1 = routers.DefaultRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('users', CustomUserViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    url('auth/', include('djoser.urls.authtoken')),
    url('', include(router_v1.urls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
