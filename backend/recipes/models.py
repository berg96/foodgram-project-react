from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, validate_slug
from django.db import models
from django.db.models import Exists, OuterRef

from .validators import validate_username

MAX_LENGTH = 200
MAX_LENGTH_COLOR = 7
MIN_VALUE_COOKING_TIME = 1
MAX_LENGTH_USER_FIELDS = 150
MAX_LENGTH_EMAIL = 254


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL, unique=True, null=False,
        verbose_name='E-mail'
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_USER_FIELDS, null=False, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_USER_FIELDS, null=False, verbose_name='Фамилия'
    )
    username = models.CharField(
        max_length=MAX_LENGTH_USER_FIELDS, unique=True,
        validators=[validate_username],
        verbose_name='Никнейм'
    )

    class Meta:
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return (f'{self.username} ({self.first_name} {self.last_name}) '
                f'- {self.email}')


class Subscribe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subs',
        verbose_name='Автор'
    )
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribes',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписку'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.subscriber.username} подписан на {self.author.username}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH, blank=False, null=False, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH, blank=False, null=False,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
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
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.slug}, {self.color})'


class RecipeQuerySet(models.QuerySet):

    def add_user_annotations(self, user_id):
        return self.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user_id=user_id,
                    recipe__pk=OuterRef('pk')
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user_id=user_id,
                    recipe__pk=OuterRef('pk')
                )
            )
        )


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
        verbose_name='Продукты'
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Теги'
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

    objects = RecipeQuerySet.as_manager()

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
        Ingredient, on_delete=models.CASCADE, verbose_name='Продукт'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(MIN_VALUE_COOKING_TIME)],
        verbose_name='Мера'
    )

    class Meta:
        verbose_name = 'Продукт в рецепте'
        verbose_name_plural = 'Продукты в рецептах'
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
