from django.contrib.auth.models import AbstractUser
from django.db import models


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
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return (f'{self.username} ({self.first_name} {self.last_name}) '
                f'- {self.email}')
