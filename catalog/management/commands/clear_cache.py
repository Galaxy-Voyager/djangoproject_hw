from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Очищает весь кеш Redis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pattern',
            type=str,
            default='skystore*',
            help='Шаблон для поиска ключей (по умолчанию: skystore*)'
        )
        parser.add_argument(
            '--product',
            type=int,
            help='Очистить кеш конкретного продукта'
        )

    def handle(self, *args, **options):
        pattern = options['pattern']
        product_id = options['product']

        if product_id:
            # Очистка кеша конкретного продукта
            keys_to_delete = [
                f'skystore:product_detail_{product_id}',
                f'skystore:products_in_category_*_{product_id}'
            ]
            deleted_count = 0

            for key in keys_to_delete:
                if cache.delete(key):
                    deleted_count += 1
                    self.stdout.write(f"Удален ключ: {key}")

            self.stdout.write(
                self.style.SUCCESS(f'Очищен кеш для продукта ID={product_id}. Удалено ключей: {deleted_count}')
            )
        else:
            # Очистка по шаблону
            cache.delete_pattern(pattern)
            self.stdout.write(
                self.style.SUCCESS(f'Кеш очищен. Шаблон: {pattern}')
            )
