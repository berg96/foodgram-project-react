import re

from django.conf import settings
from rest_framework.exceptions import ValidationError

PATTERN = r'[\w.@+-]'


def validate_username(username):
    if username == settings.SELF_PROFILE_NAME:
        raise ValidationError(
            f'Нельзя использовать "{settings.SELF_PROFILE_NAME}" '
            'в качестве username'
        )
    invalid_symbols = re.sub(PATTERN, '', username)
    if invalid_symbols:
        raise ValidationError(
            'Недопустимые символы в username: '
            f'{"".join(set(invalid_symbols))}'
        )
    return username


def validate_color(color):
    if color[0] != '#':
        raise ValidationError('Цвет должен начинаться с #')
    return color
