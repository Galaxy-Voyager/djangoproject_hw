from django.core.management.base import BaseCommand
from catalog.models import Category, Product
import json
import os


class Command(BaseCommand):
    help = 'Заполнение базы данных тестовыми продуктами и категориями'

    def handle(self, *args, **options):
        # Удаляем все существующие данные
        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write('Все существующие данные удалены')

        # Создаем категории
        categories_data = [
            {'name': 'Электроника', 'description': 'Современная техника и гаджеты'},
            {'name': 'Книги', 'description': 'Художественная и учебная литература'},
            {'name': 'Одежда', 'description': 'Модная одежда и аксессуары'},
            {'name': 'Спорт', 'description': 'Спортивные товары и инвентарь'},
            {'name': 'Мебель', 'description': 'Домашняя и офисная мебель'},
        ]

        categories = {}
        for cat_data in categories_data:
            category = Category.objects.create(**cat_data)
            categories[cat_data['name']] = category
            self.stdout.write(f'Создана категория: {category.name}')

        # Создаем продукты
        products_data = [
            {'name': 'Смартфон iPhone 15', 'description': 'Новый флагман Apple',
             'category': categories['Электроника'], 'price': 79999.99},
            {'name': 'Ноутбук Dell XPS', 'description': 'Мощный ультрабук',
             'category': categories['Электроника'], 'price': 129999.50},
            {'name': 'Наушники Sony WH-1000XM4', 'description': 'Беспроводные шумодавы',
             'category': categories['Электроника'], 'price': 29999.00},
            {'name': 'Роман "Преступление и наказание"', 'description': 'Классика Достоевского',
             'category': categories['Книги'], 'price': 1200.00},
            {'name': 'Учебник Python для начинающих', 'description': 'Основы программирования',
             'category': categories['Книги'], 'price': 2500.00},
            {'name': 'Футболка хлопковая', 'description': 'Комфортная повседневная футболка',
             'category': categories['Одежда'], 'price': 1500.00},
            {'name': 'Футбольный мяч', 'description': 'Профессиональный футбольный мяч',
             'category': categories['Спорт'], 'price': 3500.00},
            {'name': 'Офисное кресло', 'description': 'Эргономичное кресло для работы',
             'category': categories['Мебель'], 'price': 15999.99},
        ]

        for prod_data in products_data:
            product = Product.objects.create(**prod_data)
            self.stdout.write(f'Создан продукт: {product.name} - {product.price} руб.')

        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно создано: {Category.objects.count()} категорий и '
                f'{Product.objects.count()} продуктов'
            )
        )
