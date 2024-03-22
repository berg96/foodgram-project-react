from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Exists, OuterRef


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        max_length=254, unique=True, null=False,
        verbose_name='Адрес электронной почты'
    )
    first_name = models.CharField(
        max_length=150, null=False, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150, null=False, verbose_name='Фамилия'
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
        return f'{self.subscriber} подписан на {self.author}'
