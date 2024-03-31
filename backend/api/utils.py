from datetime import datetime


def create_shopping_cart(ingredients, recipes):
    return '\n'.join(
        (
            f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}',
            'Необходимые продукты:', '',
            *[
                f'{ingredient[0]}. {ingredient[1].name.capitalize()} '
                f'({ingredient[1].measurement_unit}) — '
                f'{ingredient[1].total_amount}'
                for ingredient in enumerate(ingredients, start=1)
            ],
            '', 'Перечень рецептов:', '',
            *recipes
        )
    )
