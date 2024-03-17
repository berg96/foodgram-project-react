from rest_framework.viewsets import ModelViewSet

from .serializers import IngredientSerializer
from recipes.models import Ingredient


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
