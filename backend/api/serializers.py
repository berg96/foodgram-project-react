from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Tag
from users.models import Subscribe


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.BooleanField(default=False)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_subscribed',)


class SubscriptionsSerializer(serializers.ModelSerializer):
    users = CustomUserSerializer(many=True)

    class Meta:
        model = Subscribe
        fields = ('users',)
