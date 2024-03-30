import django_filters
from django.db.models import Case, IntegerField, Q, Value, When
from rest_framework.pagination import PageNumberPagination

from recipes.models import Recipe, Tag

BOOLEAN_CHOICES = (
    ('0', False),
    ('1', True)
)


class PageNumberLimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_name')

    def filter_name(self, ingredients, name, value):
        return ingredients.filter(name__contains=value.lower()).annotate(
            sort_by=Case(
                When(Q(name__startswith=value.lower()), then=Value(1)),
                When(Q(name__contains=value.lower()), then=Value(2)),
                default=Value(3),
                output_field=IntegerField(),
            )
        ).order_by('sort_by', 'name')


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

    def filter_favorite(self, recipes, name, value):
        user = self.request.user
        if user.is_anonymous:
            return recipes
        if value == '1':
            return recipes.filter(
                id__in=(user.favorites.values_list('recipe', flat=True))
            )
        return recipes.exclude(
            id__in=(user.favorites.values_list('recipe', flat=True))
        )

    def filter_shopping_cart(self, recipes, name, value):
        user = self.request.user
        if user.is_anonymous:
            return recipes
        if value == '1':
            return recipes.filter(
                id__in=(user.shoppingcarts.values_list('recipe', flat=True))
            )
        return recipes.exclude(
            id__in=(user.shoppingcarts.values_list('recipe', flat=True))
        )
