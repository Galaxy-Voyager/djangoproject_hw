from django.core.cache import cache
from .models import Product, Category
import time


class ProductService:
    """Сервис для работы с продуктами"""

    @staticmethod
    def get_products_in_category(category_id, use_cache=True):
        """
        Возвращает все продукты в указанной категории
        с возможностью кеширования
        """
        cache_key = f'products_in_category_{category_id}'

        if use_cache:
            cached_products = cache.get(cache_key)
            if cached_products:
                print(f"Продукты категории {category_id} получены из кеша")
                return cached_products

        # Если нет в кеше или отключено кеширование
        products = Product.objects.filter(
            category_id=category_id,
            is_published=True,
            publish_status='published'
        ).select_related('category', 'owner').order_by('-created_at')
        products_list = list(products)

        if use_cache:
            cache.set(cache_key, products_list, 60 * 10)
            print(f"Продукты категории {category_id} закешированы")

        return products_list

    @staticmethod
    def get_category_with_product_count(category_id):
        """Возвращает категорию с количеством продуктов"""
        cache_key = f'category_stats_{category_id}'

        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        category = Category.objects.get(id=category_id)
        product_count = Product.objects.filter(
            category_id=category_id,
            is_published=True
        ).count()

        data = {
            'category': category,
            'product_count': product_count,
            'timestamp': time.time()
        }

        # Кешируем на 15 минут
        cache.set(cache_key, data, 60 * 15)

        return data

    @staticmethod
    def invalidate_category_cache(category_id):
        """Инвалидирует кеш для категории"""
        keys_to_delete = [
            f'products_in_category_{category_id}',
            f'category_stats_{category_id}',
        ]

        deleted_count = 0
        for key in keys_to_delete:
            if cache.delete(key):
                deleted_count += 1

        return deleted_count


def get_cached_categories():
    """Возвращает все категории с кешированием"""
    cache_key = 'all_categories'
    categories = cache.get(cache_key)

    if not categories:
        categories = Category.objects.all().order_by('name')
        cache.set(cache_key, categories, 60 * 30)  # 30 минут

    return categories
