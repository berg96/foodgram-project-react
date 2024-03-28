import re

from django.conf import settings
from rest_framework.exceptions import ValidationError

PATTERN = r'^[\w.@+-]+\Z'


def validate_username(username):
    if username == settings.SELF_PROFILE_NAME:
        raise ValidationError(
            f'Нельзя использовать "{settings.SELF_PROFILE_NAME}" '
            'в качестве username'
        )
    if not re.fullmatch(PATTERN, username):
        raise ValidationError(
            'Недопустимые символы в username: '
            f'{"".join(set(re.sub(PATTERN, "", username)))}'
        )
    return username
