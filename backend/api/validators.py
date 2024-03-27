from rest_framework.exceptions import ValidationError

from recipes.models import Recipe

NON_EXISTENT_ID_ERR_MSG = 'Указан несуществующий id'


def validate_recipe_id(pk):
    if not Recipe.objects.filter(pk=pk).exists():
        raise ValidationError({'errors': NON_EXISTENT_ID_ERR_MSG})
