from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag, User,
    Subscribe
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
    list_display = ('name', 'measurement_unit')
    list_filter = (MeasureUnitFilter,)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_color', 'slug')

    @admin.display(description='Цвет')
    @mark_safe
    def display_color(self, tag):
        return (
            f'<div style="display:flex;">{tag.color}'
            f'<div style="margin-left:10px; background-color:{tag.color}; '
            'width:30px; height:30px;"></div>'
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


class TagFilter(admin.SimpleListFilter):
    title = 'Теги'
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        return tuple(
            (
                tag.slug, f'{tag.name} ({tag.recipes.count()})'
            ) for tag in Tag.objects.all()
        )

    def queryset(self, request, recipes):
        if self.value():
            return recipes.filter(tags__slug=self.value())


class AuthorWithRecipesFilter(admin.SimpleListFilter):
    title = 'Авторы с рецептами'
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        return tuple(
            (
                author.username,
                f'{author}'.split(' -')[0] + f' ({author.recipes.count()})'
            ) for author in User.objects.filter(recipes__gte=0)
        )

    def queryset(self, request, recipes):
        if self.value():
            return recipes.filter(author__username=self.value())


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        cooking_times = model_admin.model.objects.values_list(
            'cooking_time', flat=True
        )
        fast_times = len([time for time in cooking_times if time < 10])
        medium_times = len(
            [time for time in cooking_times if time >= 10 | time < 45]
        )
        long_times = len([time for time in cooking_times if time >= 45])
        return (
            ('fast', f'быстрее 10 мин ({fast_times})'),
            ('medium', f'быстрее 45 мин ({medium_times})'),
            ('long', f'долго ({long_times})')
        )

    def queryset(self, request, recipes):
        if self.value() == 'fast':
            return recipes.filter(cooking_time__lt=10)
        if self.value() == 'medium':
            return recipes.filter(cooking_time__gte=10, cooking_time__lt=45)
        if self.value() == 'long':
            return recipes.filter(cooking_time__gte=45)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'display_image', 'name', 'author', 'display_tags',
        'display_ingredients', 'favorite_count', 'pub_time'
    )
    inlines = [RecipeIngredientInline]
    list_filter = (CookingTimeFilter, TagFilter, AuthorWithRecipesFilter)
    filter_horizontal = ('tags',)
    search_fields = ('name',)
    readonly_fields = ('favorite_count',)
    list_display_links = ('display_image', 'name')

    @admin.display(description='В избранном')
    def favorite_count(self, recipe):
        return Favorite.objects.filter(recipe=recipe).count()

    @admin.display(description='Теги')
    @mark_safe
    def display_tags(self, recipe):
        return '<br>'.join([tag.name for tag in recipe.tags.all()])

    @admin.display(description='Продукты')
    @mark_safe
    def display_ingredients(self, recipe):
        ingredients_list = '<br>'.join(
            [str(ingredient_with_amount).split(f' в {recipe.name}')[0]
             for ingredient_with_amount in
             recipe.ingredients_with_amount.all()]
        )
        return f'<div style="width: 250px;">{ingredients_list}</div>'

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
                'subscriptions',
                f'Есть подписки ({users.filter(subscriptions__gte=0).count()})'
            ),
            (
                'subscribers',
                f'Есть подписчики ({users.filter(subscribers__gte=0).count()})'
            ),
        )

    def queryset(self, request, users):
        if self.value() == 'subscriptions':
            return users.filter(subscriptions__gte=0)
        if self.value() == 'subscribers':
            return users.filter(subscribers__gte=0)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'recipes_count',
        'subscriptions_count', 'subscribers_count'
    )
    list_filter = (SubscribeFilter,)
    search_fields = ('username', 'email', 'first_name', 'last_name')

    @admin.display(description='Кол-во рецептов')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Кол-во подписок')
    def subscriptions_count(self, user):
        return user.subscriptions.count()

    @admin.display(description='Кол-во подписчиков')
    def subscribers_count(self, user):
        return user.subscribers.count()


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber')
