from rest_framework.viewsets import ModelViewSet

from .serializers import IngredientSerializer, TagSerializer
from recipes.models import Ingredient, Tag


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
