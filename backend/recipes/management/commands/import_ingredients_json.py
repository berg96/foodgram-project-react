import json

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = 'data/ingredients.json'
        with open(file_path, 'r', encoding='utf8') as file:
            data = json.load(file)
            ingredients = [Ingredient(**item) for item in data]
            Ingredient.objects.bulk_create(ingredients)
