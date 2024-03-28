from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag, User,
    Subscribe
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pub_time')
    inlines = [RecipeIngredientInline]
    list_filter = ('author', 'name', 'tags__slug')
    filter_horizontal = ('tags',)
    search_fields = ('name',)
    readonly_fields = ('favorite_count',)

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    favorite_count.short_description = (
        'Кол-во добавлений этого рецепта в избранное'
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
        return (
            ('subscriptions', 'Есть подписки'),
            ('subscribers', 'Есть подписчики'),
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
