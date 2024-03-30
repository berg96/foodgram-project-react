from datetime import datetime

import pymorphy2


def create_shopping_cart(ingredients, recipes):
    morph = pymorphy2.MorphAnalyzer()
    return '\n'.join(
        (
            f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}',
            'Необходимые продукты:', '',
            *[
                f'{index}. {name.capitalize()} — {amount} '
                f'{morph.parse(unit)[0].make_agree_with_number(amount).word}'
                if unit != 'по вкусу' else f'{index}. {name.capitalize()} — '
                                           f'{amount} {unit}'
                for index, (name, unit, amount) in enumerate(
                    ingredients.values_list(
                        'name', 'measurement_unit', 'total_amount'
                    ),
                    start=1
                )
            ],
            '', 'Перечень рецептов:', '',
            *recipes
        )
    )
