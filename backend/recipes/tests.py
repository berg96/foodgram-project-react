from django.test import TestCase

from .models import Ingredient, Tag


class IngredientModelTestCase(TestCase):
    def test_ingredient_creation(self):
        ingredient = Ingredient.objects.create(
            name='salt', measurement_unit='gr'
        )
        self.assertEqual(ingredient.name, 'salt')
        self.assertEqual(ingredient.measurement_unit, 'gr')


class TagModelTestCase(TestCase):
    def test_tag_creation(self):
        tag = Tag.objects.create(
            name='Завтрак', color='#E26C2D', slug='breakfast'
        )
        self.assertEquals(tag.name, 'Завтрак')
        self.assertEquals(tag.color, '#E26C2D')
        self.assertEquals(tag.slug, 'breakfast')
