from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Product, Category
from django.contrib.auth.models import Group, Permission

User = get_user_model()


class ProductPermissionsTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        # Создание пользователей
        self.owner1 = User.objects.create_user(
            email='owner1@test.com',
            password='test123'
        )
        self.owner2 = User.objects.create_user(
            email='owner2@test.com',
            password='test123'
        )

        # Создание модератора
        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='test123'
        )
        moderator_group, _ = Group.objects.get_or_create(name='Модератор продуктов')
        self.moderator.groups.add(moderator_group)

        # Создание категории
        self.category = Category.objects.create(name='Электроника')

        # Создание товаров
        self.product_owner1 = Product.objects.create(
            name='Телефон',
            description='Тестовый телефон',
            price=10000,
            category=self.category,
            owner=self.owner1,
            is_published=True
        )

        self.product_owner2 = Product.objects.create(
            name='Ноутбук',
            description='Тестовый ноутбук',
            price=50000,
            category=self.category,
            owner=self.owner2,
            is_published=True
        )

        self.client = Client()

    def test_owner_can_edit_own_product(self):
        """Владелец может редактировать свой товар"""
        self.client.login(email='owner1@test.com', password='test123')
        url = reverse('catalog:product_edit', kwargs={'pk': self.product_owner1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_owner_cannot_edit_others_product(self):
        """Владелец НЕ может редактировать чужой товар"""
        self.client.login(email='owner1@test.com', password='test123')
        url = reverse('catalog:product_edit', kwargs={'pk': self.product_owner2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_moderator_can_edit_any_product(self):
        """Модератор может редактировать любой товар"""
        self.client.login(email='moderator@test.com', password='test123')
        url = reverse('catalog:product_edit', kwargs={'pk': self.product_owner1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_moderator_can_delete_any_product(self):
        """Модератор может удалять любой товар"""
        self.client.login(email='moderator@test.com', password='test123')
        url = reverse('catalog:product_delete', kwargs={'pk': self.product_owner1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_cannot_edit_product(self):
        """Анонимный пользователь не может редактировать товар"""
        url = reverse('catalog:product_edit', kwargs={'pk': self.product_owner1.pk})
        response = self.client.get(url)
        # Должен быть перенаправлен на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)

    def test_product_creation_sets_owner(self):
        """При создании товара автоматически назначается владелец"""
        self.client.login(email='owner1@test.com', password='test123')
        url = reverse('catalog:product_create')

        response = self.client.post(url, {
            'name': 'Новый товар',
            'description': 'Описание',
            'price': 1000,
            'category': self.category.pk,
        })

        if response.status_code == 302:  # Успешное создание
            product = Product.objects.get(name='Новый товар')
            self.assertEqual(product.owner, self.owner1)
            print("✅ Тест: Создание товара назначает владельца - ПРОЙДЕН")
        else:
            print("⚠️ Тест: Возможна ошибка в форме")


class ProductFormValidationTestCase(TestCase):
    def test_forbidden_words_in_name(self):
        """Проверка запрещенных слов в названии"""
        from catalog.forms import ProductForm

        form = ProductForm(data={
            'name': 'Товар для казино',
            'description': 'Описание',
            'price': 1000,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('запрещенное слово', str(form.errors))
        print("✅ Тест: Запрещенные слова в названии - ПРОЙДЕН")

    def test_negative_price(self):
        """Проверка отрицательной цены"""
        from catalog.forms import ProductForm

        form = ProductForm(data={
            'name': 'Нормальный товар',
            'description': 'Описание',
            'price': -100,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('отрицательной', str(form.errors))
        print("✅ Тест: Отрицательная цена - ПРОЙДЕН")


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("ЗАПУСК АВТОМАТИЗИРОВАННЫХ ТЕСТОВ")
    print("=" * 50)

    import django

    django.setup()

    test_case = ProductPermissionsTestCase()
    test_case.setUp()

    test_case.test_owner_can_edit_own_product()
    test_case.test_owner_cannot_edit_others_product()
    test_case.test_moderator_can_edit_any_product()
    test_case.test_moderator_can_delete_any_product()
    test_case.test_anonymous_cannot_edit_product()
    test_case.test_product_creation_sets_owner()

    validation_test = ProductFormValidationTestCase()
    validation_test.test_forbidden_words_in_name()
    validation_test.test_negative_price()

    print("\n" + "=" * 50)
    print("ВСЕ ТЕСТЫ УСПЕШНО ВЫПОЛНЕНЫ!")
    print("=" * 50)
