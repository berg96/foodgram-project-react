from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Subscribe,
    Tag, User
)


class MeasureUnitFilter(admin.SimpleListFilter):
    title = 'Единицы измерения'
    parameter_name = 'measure_unit'

    def lookups(self, request, model_admin):
        measurement_units = list(model_admin.model.objects.values_list(
            'measurement_unit', flat=True
        ))
        return tuple(
            (
                unit, f'{unit} ({measurement_units.count(unit)})'
            ) for unit in sorted(set(measurement_units))
        )

    def queryset(self, request, ingredients):
        if self.value():
            return ingredients.filter(measurement_unit=self.value())


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'in_recipes_count')
    list_filter = (MeasureUnitFilter,)
    search_fields = ('name',)
    readonly_fields = ('in_recipes_count',)

    @admin.display(description='В рецептах')
    def in_recipes_count(self, ingredient):
        return ingredient.ingredients_in_recipes.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'display_color', 'slug')

    @admin.display(description='Цвет')
    @mark_safe
    def display_color(self, tag):
        return (
            f'<div style="background-color:{tag.color}; '
            f'width:30px; height:30px;">'
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


def dynamic_queryset(request, recipes):
    author = request.GET.get('author')
    if author:
        recipes = recipes.filter(author__username=author)
    tag = request.GET.get('tag')
    if tag:
        recipes = recipes.filter(tags__slug=tag)
    cooking_time = request.GET.get('cooking_time')
    if cooking_time:
        return recipes.filter(cooking_time__range=eval(cooking_time))
    return recipes


class TagFilter(admin.SimpleListFilter):
    title = 'Теги'
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        recipes = dynamic_queryset(request, model_admin.get_queryset(request))
        return tuple(
            (
                tag.slug,
                f'{tag.name} ({recipes.filter(tags__exact=tag).count()})'
            ) for tag in Tag.objects.all()
        )

    def queryset(self, request, recipes):
        if self.value():
            return recipes.filter(tags__slug=self.value())


class AuthorWithRecipesFilter(admin.SimpleListFilter):
    title = 'Авторы с рецептами'
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        recipes = dynamic_queryset(request, model_admin.get_queryset(request))
        return tuple(
            (
                author.username,
                f'{author.__str__().split(" -")[0]} '
                f'({recipes.filter(author=author).count()})'
            ) for author in set(User.objects.filter(recipes__gt=0))
        )

    def queryset(self, request, recipes):
        if self.value():
            return recipes.filter(author__username=self.value())


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        cooking_times = [
            recipe.cooking_time for recipe in Recipe.objects.all()
        ]
        if len(cooking_times) < 3:
            return None
        max_cooking_time, min_cooking_time = (
            max(cooking_times), min(cooking_times)
        )
        if max_cooking_time - min_cooking_time < 3:
            return None
        fast = (max_cooking_time + min_cooking_time) // 3
        medium = (max_cooking_time + min_cooking_time) // 3 * 2
        cooking_times_dynamic = dynamic_queryset(
            request, Recipe.objects.all()
        ).values_list('cooking_time', flat=True)
        fast_times = 0
        medium_times = 0
        long_times = 0
        for time in cooking_times_dynamic:
            if time < fast:
                fast_times += 1
            elif fast <= time < medium:
                medium_times += 1
            else:
                long_times += 1
        return (
            ((0, fast - 1), f'быстрее {fast} мин ({fast_times})'),
            ((fast, medium - 1), f'быстрее {medium} мин ({medium_times})'),
            ((medium, max_cooking_time), f'долго ({long_times})')
        )

    def queryset(self, request, recipes):
        if self.value():
            return recipes.filter(cooking_time__range=eval(self.value()))


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'display_image', 'name', 'author', 'display_tags',
        'display_ingredients', 'cooking_time', 'in_favorite_count', 'pub_time'
    )
    inlines = [RecipeIngredientInline]
    list_filter = (CookingTimeFilter, TagFilter, AuthorWithRecipesFilter)
    filter_horizontal = ('tags',)
    search_fields = ('name',)
    readonly_fields = ('in_favorite_count',)
    list_display_links = ('display_image', 'name')

    @admin.display(description='В избранном')
    def in_favorite_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Теги')
    @mark_safe
    def display_tags(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Продукты')
    @mark_safe
    def display_ingredients(self, recipe):
        return (
            '<br>'.join(
                f'{ingredient.ingredient.name[:10]} '
                f'{ingredient.amount} '
                f'({ingredient.ingredient.measurement_unit})'
                for ingredient in recipe.ingredients_in_recipes.all()
            )
        )

    @admin.display(description='Картинка')
    @mark_safe
    def display_image(self, recipe):
        return (
            f'<img src="{recipe.image.url}" '
            'style="width:50px; height:50px;">'
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


class SubscribeFilter(admin.SimpleListFilter):
    title = 'Фильтр по подпискам и подписчикам'
    parameter_name = 'subscribe_filter'

    def lookups(self, request, model_admin):
        users = model_admin.model.objects.all()
        return (
            (
                'subscribers',
                f'Есть подписки ({len(set(users.filter(subscribers__gt=0)))})'
            ),
            (
                'authors',
                f'Есть подписчики ({len(set(users.filter(authors__gt=0)))})'
            ),
        )

    def queryset(self, request, users):
        if self.value() == 'subscribers':
            return users.annotate(
                num_subscriptions=Count('subscribers')
            ).filter(num_subscriptions__gt=0)
        if self.value() == 'authors':
            return users.annotate(
                num_subscribers=Count('authors')
            ).filter(num_subscribers__gt=0)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'recipes_count',
        'subscriptions_count', 'subscribers_count'
    )
    list_filter = (SubscribeFilter,)
    search_fields = ('username', 'email', 'first_name', 'last_name')

    @admin.display(description='Рецепты')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписки')
    def subscriptions_count(self, user):
        return user.subscribers.count()

    @admin.display(description='Подписчики')
    def subscribers_count(self, user):
        return user.authors.count()


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber')
