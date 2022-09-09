import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Product

""" Основная логика команды load_data для импорта csv данных в БД"""


class Command(BaseCommand):
    """ Команда предназначена для импорта csv данных в БД"""
    def handle(self, *args, **options):
        file_path = os.path.join(
            settings.BASE_DIR, 'static/data/ingredients.csv')
        with open(file_path, encoding='utf-8') as f:
            reader = csv.reader(f)
            first_line = 1
            for row in reader:
                if first_line:
                    first_line = 0
                    continue
                Product.objects.create(
                    name=row[0],
                    measurement_unit=row[1]
                )
            f.close()
