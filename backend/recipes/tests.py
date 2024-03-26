from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)

User = get_user_model()


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


class RecipeModelTestCase(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='Author')
        self.tag = Tag.objects.create(
            name='Завтрак', color='#E26C2D', slug='breakfast'
        )
        self.ingredient_1 = Ingredient.objects.create(
            name='bread', measurement_unit='piece'
        )
        self.ingredient_2 = Ingredient.objects.create(
            name='sausage', measurement_unit='gr'
        )

    def test_recipe_creation(self):
        recipe = Recipe.objects.create(
            name='sandwich', author=self.author, cooking_time=1
        )
        recipe.tags.set([self.tag])
        RecipeIngredient.objects.create(
            ingredient=self.ingredient_1, recipe=recipe, amount=1
        )
        RecipeIngredient.objects.create(
                 ingredient=self.ingredient_2, recipe=recipe, amount=100
             )
        recipe.ingredients.set([self.ingredient_1, self.ingredient_2])
        self.assertEquals(recipe.name, 'sandwich')
        tags = recipe.tags.all()
        for tag in tags:
            self.assertEquals(tag.name, 'Завтрак')
        ingredients = recipe.ingredients.all()
        for ingredient in ingredients:
            if ingredient.name == 'bread':
                self.assertEquals(ingredient.measurement_unit, 'piece')
                self.assertEquals(RecipeIngredient.objects.get(
                    ingredient=ingredient, recipe=recipe
                ).amount, 1)
            elif ingredient.name == 'sausage':
                self.assertEquals(ingredient.measurement_unit, 'gr')
                self.assertEquals(RecipeIngredient.objects.get(
                    ingredient=ingredient, recipe=recipe
                ).amount, 100)
            else:
                self.fail('Unknown ingredient')
        self.assertEquals(recipe.cooking_time, 1)


class RecipeUserModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='User', email='user@user.com'
        )
        self.author = User.objects.create_user(
            username='Author', email='author@author.com'
        )
        self.recipe = Recipe.objects.create(
            name='sandwich', author=self.author, cooking_time=1
        )

    def test_favorite_creation(self):
        favorite_recipe = Favorite.objects.create(
            user=self.user, recipe=self.recipe
        )
        self.assertEquals(favorite_recipe.recipe.name, 'sandwich')
        self.assertEquals(favorite_recipe.user.username, 'User')

    def test_shopping_cart_creation(self):
        shopping_cart = ShoppingCart.objects.create(
            user=self.user, recipe=self.recipe
        )
        self.assertEquals(shopping_cart.recipe.name, 'sandwich')
        self.assertEquals(shopping_cart.user.username, 'User')
