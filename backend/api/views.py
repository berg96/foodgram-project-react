from djoser.views import UserViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

from .serializers import (
    IngredientSerializer, TagSerializer
)
from recipes.models import Ingredient, Tag


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
