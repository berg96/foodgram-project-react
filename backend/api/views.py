from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.models import Subscribe
from .serializers import (
    IngredientSerializer, TagSerializer, CustomUserSerializer
)
from recipes.models import Ingredient, Tag


User = get_user_model()


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'


def is_subscribed(self, user):
    return self.annotate(
        is_subscribed=Exists(
            Subscribe.objects.filter(
                subscriber=user, author__pk=OuterRef('pk')
            )
        )
    )


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return super().get_queryset()
        return is_subscribed(User.objects.all(), self.request.user)

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
        Subscribe.objects.create(
            author=author, subscriber=user
        )
        data = CustomUserSerializer(author).data
        data['is_subscribed'] = Subscribe.objects.filter(
            author=author, subscriber=user
        ).exists()
        return Response(data, status=status.HTTP_201_CREATED)

    @action(
        detail=False, methods=['get'], url_path='subscriptions',
        url_name='subscriptions'
    )
    def subscriptions(self, request):
        user = request.user
        return self.get_paginated_response(CustomUserSerializer(
            self.paginate_queryset(
                is_subscribed(User.objects.filter(
                    id__in=user.subscribes.values_list('author', flat=True)
                ), user)
            ), many=True
        ).data)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
