from datetime import datetime


def create_shopping_cart(ingredients, recipes):
    return '\n'.join(
        (
            f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}',
            'Необходимые продукты:', '',
            *[
                f'{index}. {ingredient.name.capitalize()} '
                f'— {ingredient.total_amount} ({ingredient.measurement_unit})'
                for index, ingredient in enumerate(ingredients, start=1)
            ],
            '', 'Перечень рецептов:', '',
            *recipes
        )
    )
