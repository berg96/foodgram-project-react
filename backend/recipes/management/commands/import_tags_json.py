import json

from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = 'data/tags.json'
        with open(file_path, 'r', encoding='utf8') as file:
            data = json.load(file)
            ingredients = [Tag(**item) for item in data]
            Tag.objects.bulk_create(ingredients)
