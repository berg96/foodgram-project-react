from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Exists, OuterRef, Sum

from .validators import validate_username

MAX_LENGTH = 200
MAX_LENGTH_COLOR = 7
MIN_VALUE_COOKING_TIME = 1
MIN_VALUE_AMOUNT = 1
MAX_LENGTH_USER_FIELDS = 150
MAX_LENGTH_EMAIL = 254
VALIDATE_COLOR_ERROR = 'Цвет должен быть в формате HEX-код'


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL, unique=True, verbose_name='E-mail'
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_USER_FIELDS, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_USER_FIELDS, verbose_name='Фамилия'
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
        User, on_delete=models.CASCADE, related_name='authors',
        verbose_name='Автор'
    )
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.subscriber.username} подписан на {self.author.username}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH, unique=True, verbose_name='Название'
    )
    color = models.CharField(
        max_length=MAX_LENGTH_COLOR, unique=True,
        validators=[RegexValidator(
            regex=r'^#[a-fA-F0-9]{6}\Z', message=VALIDATE_COLOR_ERROR
        )],
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH, unique=True, verbose_name='Слаг'
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
        max_length=MAX_LENGTH, verbose_name='Название'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'), verbose_name='Продукты'
    )
    tags = models.ManyToManyField(
        Tag, verbose_name='Теги'
    )
    image = models.ImageField(
        upload_to='recipes/images', verbose_name='Картинка'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(MIN_VALUE_COOKING_TIME)],
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
        default_related_name = 'recipes'

    def __str__(self):
        return f'{self.name} ({self.author.username}) {self.pub_time}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Продукт'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(MIN_VALUE_AMOUNT)],
        verbose_name='Мера'
    )

    class Meta:
        verbose_name = 'Продукт в рецепте'
        verbose_name_plural = 'Продукты в рецептах'
        ordering = ('recipe',)
        default_related_name = 'ingredients_in_recipes'

    def __str__(self):
        return (f'{self.ingredient.name} {self.amount} '
                f'{self.ingredient.measurement_unit} '
                f'в {self.recipe.name}')


class BaseUserRecipeModel(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)ss'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user_%(class)s'
            )
        ]


class Favorite(BaseUserRecipeModel):
    class Meta(BaseUserRecipeModel.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'Избранный {self.recipe.name} у {self.user.username}'


class ShoppingCart(BaseUserRecipeModel):
    class Meta(BaseUserRecipeModel.Meta):
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списках покупок'

    def __str__(self):
        return f'{self.recipe.name} у {self.user.username} в списке покупок'

    @staticmethod
    def get_ingredients_from_shopping_carts(recipes_id):
        return [
            Ingredient.objects.filter(recipes__in=recipes_id).annotate(
                total_amount=Sum('ingredients_in_recipes__amount')
            ),
            Recipe.objects.filter(id__in=recipes_id).values_list(
                'name', flat=True
            )
        ]
