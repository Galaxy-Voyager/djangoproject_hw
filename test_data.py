"""
Скрипт для создания тестовых данных
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from blog.models import BlogPost
from catalog.models import Product, Category
from users.models import User


def create_test_data():
    # Создаем группы если их нет
    from catalog.management.commands.create_groups import Command
    cmd = Command()
    cmd.handle()

    # Создаем тестового контент-менеджера
    content_manager, created = User.objects.get_or_create(
        email='content@example.com',
        defaults={
            'first_name': 'Контент',
            'last_name': 'Менеджер',
            'is_staff': True
        }
    )
    content_manager.set_password('12345')
    content_manager.save()

    # Назначаем в группу контент-менеджеров
    content_group = Group.objects.get(name='Контент-менеджер')
    content_manager.groups.add(content_group)

    # Создаем тестового модератора продуктов
    product_moderator, created = User.objects.get_or_create(
        email='moderator@example.com',
        defaults={
            'first_name': 'Модератор',
            'last_name': 'Продуктов',
            'is_staff': True
        }
    )
    product_moderator.set_password('12345')
    product_moderator.save()

    # Назначаем в группу модераторов продуктов
    moderator_group = Group.objects.get(name='Модератор продуктов')
    product_moderator.groups.add(moderator_group)

    print(" Тестовые данные созданы:")
    print(f"   - Контент-менеджер: content@example.com / 12345")
    print(f"   - Модератор продуктов: moderator@example.com / 12345")
    print(f"   - Обычный пользователь: создайте через форму регистрации")


if __name__ == '__main__':
    create_test_data()
