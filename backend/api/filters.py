import django_filters
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination

from recipes.models import Recipe, Tag

BOOLEAN_CHOICES = (
    ('0', False),
    ('1', True)
)


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='author__id')
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(), to_field_name='slug',
        field_name='tags__slug'
    )
    is_favorited = django_filters.ChoiceFilter(
        method='filter_favorite', choices=BOOLEAN_CHOICES
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        method='filter_shopping_cart', choices=BOOLEAN_CHOICES
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_favorite(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset
        if value == '1':
            return queryset.filter(
                id__in=(user.favorites.values_list('recipe', flat=True))
            )
        return queryset.exclude(
            id__in=(user.favorites.values_list('recipe', flat=True))
        )

    def filter_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset
        if value == '1':
            return queryset.filter(
                id__in=(user.shopping_carts.values_list('recipe', flat=True))
            )
        return queryset.exclude(
            id__in=(user.shopping_carts.values_list('recipe', flat=True))
        )
