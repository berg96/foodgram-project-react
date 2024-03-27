import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from users.models import Subscribe


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class SimpleRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            return Subscribe.objects.filter(
                author=obj, subscriber=self.context['request'].user
            ).exists()
        return False


class SubscribeSerializer(CustomUserSerializer):
    recipes = SimpleRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        if recipes_limit is not None:
            representation['recipes'] = (
                representation['recipes'][:int(recipes_limit)]
            )
        return representation


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=obj), many=True
        ).data

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_authenticated:
            return Favorite.objects.filter(
                recipe=obj, user=self.context['request'].user
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            return ShoppingCart.objects.filter(
                recipe=obj, user=self.context['request'].user
            ).exists()
        return False
