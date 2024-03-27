from django.contrib import admin

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
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
