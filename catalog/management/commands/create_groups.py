from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Создает группы с правами для проекта'

    def handle(self, *args, **options):
        # Получаем ContentType для моделей
        product_content_type = ContentType.objects.get_for_model(Product)
        blogpost_content_type = ContentType.objects.get_for_model(BlogPost)

        # Получаем все разрешения для моделей
        product_permissions = Permission.objects.filter(content_type=product_content_type)
        blogpost_permissions = Permission.objects.filter(content_type=blogpost_content_type)

        # 1. Группа "Модератор продуктов"
        moderator_group, created = Group.objects.get_or_create(name='Модератор продуктов')

        # Права для модератора продуктов:
        can_unpublish = Permission.objects.get(
            codename='can_unpublish_product',
            content_type=product_content_type
        )

        delete_product = Permission.objects.get(
            codename='delete_product',
            content_type=product_content_type
        )

        change_product = Permission.objects.get(
            codename='change_product',
            content_type=product_content_type
        )

        view_product = Permission.objects.get(
            codename='view_product',
            content_type=product_content_type
        )

        moderator_group.permissions.add(
            can_unpublish,
            delete_product,
            change_product,
            view_product
        )

        # 2. Группа "Контент-менеджер"
        content_manager_group, created = Group.objects.get_or_create(name='Контент-менеджер')

        # Права для контент-менеджера (все права на BlogPost)
        for perm in blogpost_permissions:
            content_manager_group.permissions.add(perm)

        # Добавляем кастомное право для управления блогом
        can_manage_blog = Permission.objects.get(
            codename='can_manage_blog',
            content_type=blogpost_content_type
        )
        content_manager_group.permissions.add(can_manage_blog)

        # Контент-менеджер также может просматривать продукты
        content_manager_group.permissions.add(view_product)

        # 3. Группа "Владельцы продуктов"
        owner_group, created = Group.objects.get_or_create(name='Владельцы продуктов')

        self.stdout.write(
            self.style.SUCCESS('✅ Группы успешно созданы:')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   - Модератор продуктов: {moderator_group.permissions.count()} прав')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   - Контент-менеджер: {content_manager_group.permissions.count()} прав')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   - Владельцы продуктов: {owner_group.permissions.count()} прав')
        )

        # Выводим информацию о правах
        self.stdout.write('\nПрава контент-менеджера:')
        for perm in content_manager_group.permissions.all():
            self.stdout.write(f'   - {perm.name}')
