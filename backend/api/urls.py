from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from .views import IngredientViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    url('', include(router_v1.urls)),
]
