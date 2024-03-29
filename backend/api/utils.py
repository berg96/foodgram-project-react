from collections import defaultdict


def create_shopping_cart(ingredients):
    shopping_cart = defaultdict(int)
    ingredient_unit = {}
    recipes = []
    for ingredient in ingredients:
        shopping_cart[ingredient.ingredient.name] += ingredient.amount
        recipes.append(ingredient.recipe.name)
        ingredient_unit[
            ingredient.ingredient.name
        ] = ingredient.ingredient.measurement_unit
    ingredients = [
        (
            f'{index + 1}. {ingredient.capitalize()} — '
            f'{shopping_cart[ingredient]} {ingredient_unit[ingredient]}'
        )
        for index, ingredient in enumerate(shopping_cart)
    ]
    return '\n'.join(
        (
            'Необходимые продукты:\n', *ingredients,
            '\nПеречень рецептов:\n', *recipes
        )
    )
