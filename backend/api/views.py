from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Subscribe, Tag
)

from .filters import IngredientFilter, PageNumberLimitPagination, RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (
    IngredientSerializer, RecipeReadSerializer, RecipeWriteSerializer,
    SimpleRecipeSerializer, SubscribeSerializer, TagSerializer,
    UserWithSubscriptionSerializer
)
from .utils import create_shopping_cart

User = get_user_model()

DOUBLE_SUBSCRIBE_ERROR = 'Вы уже подписаны на {}'
SUBSCRIBE_SELF_ERROR = 'Нельзя подписаться на самого себя'
RECIPE_NOT_FOUND_ERROR = 'Этого рецепта нет в {}'
RECIPE_IS_ALREADY_IN_ERROR = 'Этот рецепт уже есть в {}'
NOT_AUTHENTICATED_ERROR = 'Учетные данные не были предоставлены.'


class UserWithSubscriptionViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserWithSubscriptionSerializer
    pagination_class = PageNumberLimitPagination

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return super().get_queryset()
        return User.objects.annotate(
            is_subscribed=Exists(
                Subscribe.objects.filter(
                    subscriber=self.request.user,
                    author_id=OuterRef('id')
                )
            )
        )

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=True, methods=['post', 'delete'], url_path='subscribe',
        url_name='subscribe', permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        user = request.user
        if request.method == 'DELETE':
            get_object_or_404(
                Subscribe, author=author, subscriber=user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        _, flag = Subscribe.objects.get_or_create(
            author=author, subscriber=user
        )
        if not flag:
            raise ValidationError(
                {'errors': DOUBLE_SUBSCRIBE_ERROR.format(author.username)}
            )
        if author == user:
            raise ValidationError(
                {'errors': SUBSCRIBE_SELF_ERROR}
            )
        data = SubscribeSerializer(author, context={
            'recipes_limit': request.GET.get('recipes_limit', 10**10)
        }).data
        data['is_subscribed'] = True
        return Response(data, status.HTTP_201_CREATED)

    @action(
        detail=False, methods=['get'], url_path='subscriptions',
        url_name='subscriptions', permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        return self.get_paginated_response(SubscribeSerializer(
            self.paginate_queryset(self.get_queryset().filter(
                id__in=user.subscriptions.values_list('author', flat=True)
            )), many=True,
            context={
                'recipes_limit': request.GET.get('recipes_limit', 10**10)
            }
        ).data)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None
    http_method_names = ['get']


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ['get']


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberLimitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [AuthorOrReadOnly]

    def get_queryset(self):
        return Recipe.objects.add_user_annotations(self.request.user.pk)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated(
                {'detail': NOT_AUTHENTICATED_ERROR},
            )
        serializer.save(author=user)

    def create_delete_for_recipe(self, request, model, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        user = request.user
        if request.method == 'DELETE':
            get_object_or_404(model, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'errors': RECIPE_IS_ALREADY_IN_ERROR.format('избранных')}
            )
        model.objects.create(user=user, recipe=recipe)
        return Response(
            SimpleRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True, methods=['post', 'delete'], url_path='favorite',
        url_name='favorite', permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.create_delete_for_recipe(request, Favorite, pk)

    @action(
        detail=True, methods=['post', 'delete'], url_path='shopping_cart',
        url_name='shoppingcart', permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.create_delete_for_recipe(request, ShoppingCart, pk)

    @action(
        detail=False, methods=['get'], url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        return FileResponse(
            create_shopping_cart(
                ShoppingCart.get_ingredients_from_shopping_carts(
                    self, request.user
                )
            ),
            as_attachment=True, filename='shopping_cart.txt',
            content_type='text/plain'
        )
