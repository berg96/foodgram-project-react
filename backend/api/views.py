import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import CustomPagination, IngredientSearchFilter, RecipeFilter
from .permissions import AuthorAdminOrReadOnly
from .serializers import (
    CustomUserSerializer, IngredientSerializer, RecipeSerializer,
    SimpleRecipeSerializer, SubscribeSerializer, TagSerializer
)
from .validators import validate_recipe_id, validate_tags_and_ingredients
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from users.models import Subscribe

User = get_user_model()

UNSUBSCRIBE_ERR_MSG = 'Вы не подписаны на {}'
DOUBLE_SUBSCRIBE_ERR_MSG = 'Вы уже подписаны на {}'
SUBSCRIBE_SELF_ERR_MSG = 'Нельзя подписаться на самого себя'
RECIPE_IS_NOT_IN = 'Этого рецепта нет в {}'
RECIPE_IS_ALREADY_IN = 'Этот рецепт уже есть в {}'


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=False, url_path=settings.SELF_PROFILE_NAME,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        return Response(CustomUserSerializer(
            request.user, context={'request': request}
        ).data)

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
                raise ValidationError(
                    {'errors': UNSUBSCRIBE_ERR_MSG.format(author.username)}
                )
            Subscribe.objects.filter(author=author, subscriber=user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if Subscribe.objects.filter(author=author, subscriber=user).exists():
            raise ValidationError(
                {'errors': DOUBLE_SUBSCRIBE_ERR_MSG.format(author.username)}
            )
        if author == user:
            raise ValidationError(
                {'errors': SUBSCRIBE_SELF_ERR_MSG}
            )
        Subscribe.objects.create(author=author, subscriber=user)
        return Response(
            SubscribeSerializer(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=False, methods=['get'], url_path='subscriptions',
        url_name='subscriptions', permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        return self.get_paginated_response(SubscribeSerializer(
            self.paginate_queryset(User.objects.filter(
                id__in=user.subscribes.values_list('author', flat=True)
            )), many=True, context={'request': request}
        ).data)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None
    http_method_names = ['get']


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ['get']


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [AuthorAdminOrReadOnly]

    def perform_create(self, serializer):
        tags_id = self.request.data.get('tags')
        ingredients = self.request.data.get('ingredients')
        validate_tags_and_ingredients(tags_id, ingredients)
        serializer.save(
            author=self.request.user, tags=Tag.objects.filter(id__in=tags_id)
        )
        ingredients_id = []
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=serializer.instance,
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                amount=ingredient['amount']
            )
            ingredients_id.append(ingredient['id'])
        serializer.save(
            ingredients=Ingredient.objects.filter(id__in=ingredients_id)
        )

    def perform_update(self, serializer):
        tags_id = self.request.data.get('tags')
        ingredients = self.request.data.get('ingredients')
        validate_tags_and_ingredients(tags_id, ingredients)
        recipe = serializer.instance
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        ingredients_id = []
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                amount=ingredient['amount']
            )
            ingredients_id.append(ingredient['id'])
        serializer.save(
            ingredients=Ingredient.objects.filter(id__in=ingredients_id),
            tags=Tag.objects.filter(id__in=tags_id)
        )

    @action(
        detail=True, methods=['post', 'delete'], url_path='favorite',
        url_name='favorite', permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        user = request.user
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            if not Favorite.objects.filter(
                    user=user, recipe=recipe
            ).exists():
                raise ValidationError(
                    {'errors': RECIPE_IS_NOT_IN.format('избранных')}
                )
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        validate_recipe_id(pk)
        recipe = get_object_or_404(Recipe, pk=pk)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'errors': RECIPE_IS_ALREADY_IN.format('избранных')}
            )
        Favorite.objects.create(user=user, recipe=recipe)
        return Response(
            SimpleRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True, methods=['post', 'delete'], url_path='shopping_cart',
        url_name='shoppingcart', permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        user = request.user
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            if not Favorite.objects.filter(
                    user=user, recipe=recipe
            ).exists():
                raise ValidationError(
                    {'errors': RECIPE_IS_NOT_IN.format('списке покупок')}
                )
            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        validate_recipe_id(pk)
        recipe = get_object_or_404(Recipe, pk=pk)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'errors': RECIPE_IS_ALREADY_IN.format('списке покупок')}
            )
        ShoppingCart.objects.create(user=user, recipe=recipe)
        return Response(
            SimpleRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    @action(
        detail=False, methods=['get'], url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=user.shopping_carts.values_list('recipe', flat=True)
        )
        shopping_cart = ''
        for ingredient in ingredients:
            shopping_cart += (
                f'{ingredient.ingredient} — {ingredient.amount}\n'
            )
        with tempfile.NamedTemporaryFile(
                suffix='.txt', delete=False
        ) as temp_file:
            temp_file.write(shopping_cart[:-1].encode('utf-8'))
        response = FileResponse(open(temp_file.name, 'rb'))
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response
