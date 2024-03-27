import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

EMPTY_FIELD_ERR_MSG = 'Поле имеет пустое значение'
REPETITIVE_ID_ERR_MSG = 'Содержатся повторяющиеся значения id'


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
    is_subscribed = serializers.BooleanField(read_only=True, default=False)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_subscribed',)


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
        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit:
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


class RecipeReadSerializer(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True, default=False
    )
    image = Base64ImageField()
    tags = TagSerializer(many=True)
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


class IngredientAmountSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    ingredients = IngredientAmountSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )

    class Meta:
        model = Recipe
        fields = (
            'tags', 'ingredients', 'image', 'name', 'text', 'cooking_time'
        )

    def validate_tags(self, value):
        if len(value) < 1:
            raise serializers.ValidationError([EMPTY_FIELD_ERR_MSG])
        if len(value) != len(set(value)):
            raise serializers.ValidationError([REPETITIVE_ID_ERR_MSG])
        return value

    def validate_ingredients(self, value):
        if len(value) < 1:
            raise serializers.ValidationError([EMPTY_FIELD_ERR_MSG])
        if len(value) != len(set([item['id'] for item in value])):
            raise serializers.ValidationError([REPETITIVE_ID_ERR_MSG])
        return value

    def to_representation(self, instance):
        return RecipeReadSerializer(instance).data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        create_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(create_ingredients)
        return recipe

    def update(self, instance, validated_data):
        error = {}
        tags = validated_data.pop('tags', None)
        if not tags:
            error['tags'] = [EMPTY_FIELD_ERR_MSG]
        ingredients = validated_data.pop('ingredients', None)
        if not ingredients:
            error['ingredients'] = [EMPTY_FIELD_ERR_MSG]
        if error:
            raise serializers.ValidationError(error)
        instance.ingredients.clear()
        create_ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(create_ingredients)
        return super().update(instance, validated_data)
