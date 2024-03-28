import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = 'data/ingredients.csv'
        with open(file_path, 'r', encoding='utf8') as file:
            reader = csv.reader(file)
            ingredients = [
                Ingredient(
                    name=row[0], measurement_unit=row[1]
                )
                for row in reader
            ]
            Ingredient.objects.bulk_create(ingredients)
