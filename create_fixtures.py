import os
import django
import json
from decimal import Decimal


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Category, Product
from django.core.serializers import serialize


def create_fixtures():
    categories = Category.objects.all()
    category_fixture = json.loads(serialize('json', categories, indent=2))


    products = Product.objects.all()
    product_fixture = json.loads(serialize('json', products, indent=2))


    with open('catalog/fixtures/category_data.json', 'w', encoding='utf-8') as f:
        json.dump(category_fixture, f, indent=2, ensure_ascii=False)

    with open('catalog/fixtures/product_data.json', 'w', encoding='utf-8') as f:
        json.dump(product_fixture, f, indent=2, ensure_ascii=False)

    print("Фикстуры созданы")
    print(f"Категории: {len(category_fixture)} записей")
    print(f"Продукты: {len(product_fixture)} записей")


if __name__ == "__main__":
    create_fixtures()
