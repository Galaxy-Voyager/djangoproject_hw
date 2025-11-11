from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Поля для отображения в списке
    list_display_links = ('id', 'name')  # Поля-ссылки для редактирования
    search_fields = ('name', 'description')  # Поля для поиска


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category')  # Поля в списке
    list_display_links = ('id', 'name')  # Поля-ссылки
    list_filter = ('category',)  # Фильтрация по категории
    search_fields = ('name', 'description')  # Поиск по названию и описанию
    list_per_page = 20  # Количество элементов на странице
