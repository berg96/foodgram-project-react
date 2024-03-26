from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, validate_slug
from django.db import models

User = get_user_model()

MAX_LENGTH = 200
MAX_LENGTH_COLOR = 7
MIN_VALUE_COOKING_TIME = 1


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH, blank=False, null=False, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH, blank=False, null=False,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH, blank=False, null=False, unique=True,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=MAX_LENGTH_COLOR, blank=False, null=False, unique=True,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH, blank=False, null=False, unique=True,
        validators=[validate_slug], verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.slug}, {self.color})'


class Recipe(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH, blank=False, null=False, verbose_name='Название'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'), related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Тэги'
    )
    image = models.ImageField(
        upload_to='recipes/images', blank=False, null=False,
        verbose_name='Картинка'
    )
    text = models.TextField(blank=False, null=False, verbose_name='Описание')
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)], blank=False, null=False,
        verbose_name='Время приготовления'
    )
    pub_time = models.DateTimeField(
        auto_now_add=True, verbose_name='Время публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_time',)

    def __str__(self):
        return f'{self.name} ({self.author.username}) {self.pub_time}'


class BaseRecipeModel(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )

    class Meta:
        abstract = True


class RecipeIngredient(BaseRecipeModel):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(MIN_VALUE_COOKING_TIME)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        ordering = ('recipe',)

    def __str__(self):
        return (f'{self.amount} {self.ingredient.measurement_unit} '
                f'{self.ingredient.name} в {self.recipe.name}')


class Favorite(BaseRecipeModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('user',)

    def __str__(self):
        return f'Избранный {self.recipe.name} у {self.user.username}'


class ShoppingCart(BaseRecipeModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_carts',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списках покупок'
        ordering = ('user',)

    def __str__(self):
        return f'{self.recipe.name} у {self.user.username} в списке покупок'
