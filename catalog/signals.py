from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, Category
from .services import ProductService


@receiver(post_save, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    """Инвалидирует кеш при сохранении продукта"""
    # Очищаем кеш продукта
    cache.delete(f'product_detail_{instance.pk}')

    # Очищаем кеш категории этого продукта
    if instance.category_id:
        ProductService.invalidate_category_cache(instance.category_id)

    # Очищаем кеш главной страницы
    cache.delete('home_products_list')

    print(f"Кеш инвалидирован для продукта: {instance.name}")


@receiver(post_delete, sender=Product)
def invalidate_product_cache_on_delete(sender, instance, **kwargs):
    """Инвалидирует кеш при удалении продукта"""
    # Очищаем кеш продукта
    cache.delete(f'product_detail_{instance.pk}')

    # Очищаем кеш категории
    if instance.category_id:
        ProductService.invalidate_category_cache(instance.category_id)

    # Очищаем кеш главной страницы
    cache.delete('home_products_list')

    print(f"Кеш инвалидирован после удаления продукта: {instance.name}")


@receiver(post_save, sender=Category)
def invalidate_category_cache(sender, instance, **kwargs):
    """Инвалидирует кеш при изменении категории"""
    # Очищаем кеш категорий
    cache.delete('all_categories')

    # Очищаем кеш продуктов в этой категории
    ProductService.invalidate_category_cache(instance.pk)

    print(f"Кеш инвалидирован для категории: {instance.name}")
