from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

EMPTY_FIELD_ERROR = 'Поле имеет пустое значение'
DUPLICATE_ID_ERROR = 'Содержатся повторяющиеся значения id: {}'


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


class UserWithSubscriptionSerializer(UserSerializer):
    is_subscribed = serializers.BooleanField(read_only=True, default=False)

    class Meta(UserSerializer.Meta):
        fields = (*UserSerializer.Meta.fields, 'is_subscribed',)


class SubscribeSerializer(UserWithSubscriptionSerializer):
    recipes = SimpleRecipeSerializer(many=True)
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta(UserWithSubscriptionSerializer.Meta):
        fields = (
            *UserWithSubscriptionSerializer.Meta.fields, 'recipes',
            'recipes_count'
        )

    def to_representation(self, user):
        representation = super().to_representation(user)
        representation['recipes'] = (
            representation['recipes'][:self.context['recipes_limit']]
        )
        return representation


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=1)

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
    ingredients = RecipeIngredientSerializer(
        many=True, source='ingredients_in_recipes'
    )
    author = UserWithSubscriptionSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    ingredients = RecipeIngredientSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )

    class Meta:
        model = Recipe
        fields = (
            'tags', 'ingredients', 'image', 'name', 'text', 'cooking_time'
        )

    @staticmethod
    def validate_tags_ingredients(values):
        if len(values) < 1:
            raise serializers.ValidationError([EMPTY_FIELD_ERROR])
        duplicated_ids = [
            str(item.id) for item in values if values.count(item) > 1
        ]
        if duplicated_ids:
            raise serializers.ValidationError(
                [DUPLICATE_ID_ERROR.format(id) for id in set(duplicated_ids)]
            )
        return values

    def validate_tags(self, tags):
        return self.validate_tags_ingredients(tags)

    def validate_ingredients(self, ingredients):
        self.validate_tags_ingredients(
            [ingredient['ingredient'] for ingredient in ingredients]
        )
        return ingredients

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(EMPTY_FIELD_ERROR)
        return image

    def to_representation(self, recipe):
        return RecipeReadSerializer(recipe).data

    @staticmethod
    def create_recipe_ingredients(recipe, ingredients):
        RecipeIngredient.objects.bulk_create(RecipeIngredient(
            recipe=recipe,
            ingredient=ingredient['ingredient'],
            amount=ingredient['amount']
        ) for ingredient in ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_recipe_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        error = {}
        tags = validated_data.pop('tags', None)
        if not tags:
            error['tags'] = [EMPTY_FIELD_ERROR]
        ingredients = validated_data.pop('ingredients', None)
        if not ingredients:
            error['ingredients'] = [EMPTY_FIELD_ERROR]
        if error:
            raise serializers.ValidationError(error)
        recipe.tags.set(tags)
        recipe.ingredients.clear()
        self.create_recipe_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)
