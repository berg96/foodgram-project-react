from django.test import TestCase

from .models import Ingredient


class IngredientModelTestCase(TestCase):
    def test_ingredient_creation(self):
        ingredient = Ingredient.objects.create(
            name='salt', measurement_unit='gr'
        )
        self.assertEqual(ingredient.name, 'salt')
        self.assertEqual(ingredient.measurement_unit, 'gr')
