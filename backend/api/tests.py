from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITransactionTestCase

from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient
from users.models import Subscribe


User = get_user_model()


class IngredientApiTestCase(APITransactionTestCase):
    def setUp(self):
        self.ingredient = Ingredient.objects.create(
            name='salt', measurement_unit='gr',
        )

    def test_list(self):
        response = self.client.get(reverse('ingredients-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(
            response.data['results'][0]['name'], self.ingredient.name
        )


class TagApiTestCase(APITransactionTestCase):
    def setUp(self):
        self.tag = Tag.objects.create(
            name='Завтрак', color='#E26C2D', slug='breakfast'
        )

    def test_list(self):
        response = self.client.get(reverse('tags-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['results'][0]['name'], self.tag.name)


class UserApiTestCase(APITransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user', email='user@user.com'
        )
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.author = User.objects.create_user(
            username='author', email='author@author.com'
        )
        Subscribe.objects.create(author=self.author, subscriber=self.user)

    def test_list(self):
        response = self.client.get(reverse('users-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 2)
        self.assertEquals(
            response.data['results'][0]['username'], self.author.username
        )

    def test_subscriptions(self):
        response = self.client.get(reverse('users-subscriptions'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(
            response.data['results'][0]['username'], self.author.username
        )
        self.assertTrue(response.data['results'][0]['is_subscribed'])


class RecipeApiTestCase(APITransactionTestCase):
    def setUp(self):
        self.ingredient_1 = Ingredient.objects.create(
            name='salt', measurement_unit='gr',
        )
        self.ingredient_2 = Ingredient.objects.create(
            name='bread', measurement_unit='piece',
        )
        self.tag = Tag.objects.create(
            name='Завтрак', color='#E26C2D', slug='breakfast'
        )
        self.user = User.objects.create_user(
            username='user', email='user@user.com'
        )
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.recipe = Recipe.objects.create(
            name='bread with salt', author=self.user, cooking_time=1
        )
        self.recipe.tags.set([self.tag])
        self.recipeingredient_1 = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient_1, amount=100
        )
        self.recipeingredient_2 = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient_2, amount=1
        )
        self.recipe.ingredients.set([self.ingredient_1, self.ingredient_2])

    def test_list(self):
        response = self.client.get(reverse('recipes-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 1)
        self.assertEquals(
            response.data['results'][0]['name'], self.recipe.name
        )
