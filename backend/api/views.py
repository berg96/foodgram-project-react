import json
import tempfile
from collections import defaultdict

from django.contrib.auth import get_user_model
from django.http import FileResponse
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.models import Subscribe
from .serializers import (
    IngredientSerializer, TagSerializer, CustomUserSerializer,
    RecipeSerializer, SimpleRecipeSerializer
)
from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient, Favorite, \
    ShoppingCart

User = get_user_model()


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True, methods=['post', 'delete'], url_path='subscribe',
        url_name='subscribe'
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        user = request.user
        if request.method == 'DELETE':
            if not Subscribe.objects.filter(
                    author=author, subscriber=user
            ).exists():
                return Response(
                    {'errors': f'Вы не подписаны на {author.username}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.filter(author=author, subscriber=user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if Subscribe.objects.filter(author=author, subscriber=user).exists():
            return Response(
                {'errors': f'Вы уже подписаны на {author.username}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if author == user:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscribe.objects.create(author=author, subscriber=user)
        return Response(
            CustomUserSerializer(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=False, methods=['get'], url_path='subscriptions',
        url_name='subscriptions'
    )
    def subscriptions(self, request):
        user = request.user
        return self.get_paginated_response(CustomUserSerializer(
            self.paginate_queryset(User.objects.filter(
                id__in=user.subscribes.values_list('author', flat=True)
            )
            ), many=True, context={'request': request}
        ).data)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        tags_id = self.request.data['tags']
        tags = Tag.objects.filter(id__in=tags_id)
        serializer.save(author=self.request.user, tags=tags)
        ingredients = self.request.data['ingredients']
        ingredients_id = []
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=get_object_or_404(
                    Recipe, name=self.request.data['name']
                ),
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                amount=ingredient['amount']
            )
            ingredients_id.append(ingredient['id'])
        serializer.save(
            ingredients=Ingredient.objects.filter(id__in=ingredients_id)
        )

    def perform_update(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        tags_id = self.request.data.get('tags')
        if tags_id:
            tags = Tag.objects.filter(id__in=tags_id)
            serializer.save(tags=tags)
        ingredients = self.request.data.get('ingredients')
        if ingredients:
            RecipeIngredient.objects.filter(recipe=recipe).delete()
            ingredients_id = []
            for ingredient in ingredients:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        Ingredient, id=ingredient['id']
                    ),
                    amount=ingredient['amount']
                )
                ingredients_id.append(ingredient['id'])
            serializer.save(
                ingredients=Ingredient.objects.filter(id__in=ingredients_id)
            )

    @action(
        detail=True, methods=['post', 'delete'], url_path='favorite',
        url_name='favorite'
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'DELETE':
            if not Favorite.objects.filter(
                    user=user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Этого рецепта нет в избранных'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Этот рецепт уже есть в избранных'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(user=user, recipe=recipe)
        return Response(
            SimpleRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True, methods=['post', 'delete'], url_path='shopping_cart',
        url_name='shoppingcart'
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'DELETE':
            if not Favorite.objects.filter(
                    user=user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Этого рецепта нет в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Этот рецепт уже есть в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(user=user, recipe=recipe)
        return Response(
            SimpleRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=user.shopping_carts.values_list('recipe', flat=True)
        )
        shopping_cart = defaultdict(int)
        for ingredient in ingredients:
            shopping_cart[ingredient.ingredient.name] += ingredient.amount
        with tempfile.NamedTemporaryFile(
                suffix='.txt', delete=False
        ) as temp_file:
            temp_file.write(json.dumps(dict(shopping_cart)).encode('utf-8'))
        response = FileResponse(open(temp_file.name, 'rb'))
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response
