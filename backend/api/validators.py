from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, Recipe, Tag

EMPTY_FIELD_ERR_MSG = 'Нет поля или имеет пустое значение'
NON_EXISTENT_ID_ERR_MSG = 'Указан несуществующий id'
INVALID_VALUE_ERR_MSG = 'Указано неверное значение'


def validate_tags_and_ingredients(tags_id, ingredients):
    error = {}
    if not tags_id:
        error['tags'] = [EMPTY_FIELD_ERR_MSG]
    if not ingredients:
        error['ingredients'] = [EMPTY_FIELD_ERR_MSG]
    if error:
        raise ValidationError(error)
    if len(tags_id) != Tag.objects.filter(id__in=tags_id).count():
        raise ValidationError({'tags': [NON_EXISTENT_ID_ERR_MSG]})
    ingredients_id = []
    for ingredient in ingredients:
        if ingredient['amount'] < 1:
            raise ValidationError({'amount': [INVALID_VALUE_ERR_MSG]})
        ingredients_id.append(ingredient['id'])
    if len(ingredients_id) != Ingredient.objects.filter(
            id__in=ingredients_id
    ).count():
        raise ValidationError({'ingredients': [NON_EXISTENT_ID_ERR_MSG]})


def validate_recipe_id(pk):
    if not Recipe.objects.filter(pk=pk).exists():
        raise ValidationError({'errors': NON_EXISTENT_ID_ERR_MSG})
