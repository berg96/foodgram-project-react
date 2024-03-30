import re

from django.conf import settings
from django.core.exceptions import ValidationError

PATTERN = r'[\w.@+-]'

USERNAME_ERROR_MESSAGE = 'Нельзя использовать "{}" в качестве username'
USERNAME_INVALID_CHARACTERS_ERROR = 'Недопустимые символы в username: {}'
COLOR_FORMAT_ERROR = 'Цвет должен начинаться с #'


def validate_username(username):
    if username == settings.SELF_PROFILE_NAME:
        raise ValidationError(
            USERNAME_ERROR_MESSAGE.format(settings.SELF_PROFILE_NAME)
        )
    invalid_characters = re.sub(PATTERN, '', username)
    if invalid_characters:
        raise ValidationError(
            USERNAME_INVALID_CHARACTERS_ERROR.format(
                "".join(set(invalid_characters))
            )
        )
    return username
