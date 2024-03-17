from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from recipes.models import Ingredient, Tag


class IngredientApiTestCase(APITransactionTestCase):
    def setUp(self):
        self.ingredient = Ingredient.objects.create(
            name='salt', measurement_unit='gr',
        )

    def test_list(self):
        response = self.client.get(reverse('ingredients-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data[0]['name'], self.ingredient.name)


class TagApiTestCase(APITransactionTestCase):
    def setUp(self):
        self.tag = Tag.objects.create(
            name='Завтрак', color='#E26C2D', slug='breakfast'
        )

    def test_list(self):
        response = self.client.get(reverse('tags-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data[0]['name'], self.tag.name)

