from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from .models import Product, Category
from .forms import ProductForm
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.db.models import Q
from .services import ProductService, get_cached_categories
import time


class HomeListView(ListView):
    """CBV для главной страницы с пагинацией и кешированием"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 6
    ordering = ['-created_at']

    # Время кеширования (в секундах)
    cache_timeout = 60 * 10  # 10 минут

    def get_queryset(self):
        """Получаем кешированный QuerySet продуктов"""
        cache_key = 'home_products_list'

        # Пытаемся получить из кеша
        cached_queryset = cache.get(cache_key)

        if cached_queryset is not None:
            print("Список продуктов получен из кеша")
            return cached_queryset

        # Если нет в кеше - выполняем запрос
        queryset = Product.objects.filter(
            is_published=True,
            publish_status='published'
        ).select_related('category', 'owner').order_by(*self.ordering)

        # Сохраняем в кеш
        cache.set(cache_key, queryset, self.cache_timeout)
        print("Список продуктов закеширован")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Skystore - Главная'
        context['cache_timeout'] = self.cache_timeout
        context['cache_info'] = {
            'cached_at': time.time(),
            'products_count': self.get_queryset().count()
        }

        # Получаем кешированные категории
        from .services import get_cached_categories
        context['categories'] = get_cached_categories()

        # Статистика кеша (для отладки)
        if self.request.user.is_staff:
            context['cache_stats'] = self.get_cache_stats()

        return context

    def get_cache_stats(self):
        """Статистика кеша (только для администраторов)"""
        cache_stats = {}

        # Проверяем кеш главной страницы
        cache_key = 'home_products_list'
        ttl = cache.ttl(cache_key)

        if ttl:
            cache_stats['home_cache'] = dict(ttl=ttl, ttl_minutes=ttl // 60, is_active=True)
        else:
            cache_stats['home_cache'] = {'is_active': False}

        # Проверяем кеш Redis
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            cache_stats['redis_info'] = redis_conn.info()
        except Exception as e:
            cache_stats['redis_error'] = str(e)

        return cache_stats


class ProductDetailView(DetailView):
    """CBV для детальной страницы товара"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    # Время кеширования в секундах (5 минут)
    cache_timeout = 60 * 5

    def get_object(self, queryset=None):
        """Получаем объект с кешированием"""
        cache_key = f'product_detail_{self.kwargs.get("pk")}'
        product = cache.get(cache_key)

        if not product:
            product = super().get_object(queryset)
            # Кешируем на указанное время
            cache.set(cache_key, product, self.cache_timeout)
            print(f"Продукт {product.name} закеширован на {self.cache_timeout} секунд")

        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.name} - Skystore'
        context['cache_timeout'] = self.cache_timeout
        context['cached_at'] = time.time()
        return context


# Альтернативный способ с декоратором (можно использовать вместо get_object)
@method_decorator(cache_page(60 * 5), name='dispatch')
class ProductDetailViewCached(DetailView):
    """Версия с декоратором кеширования всей страницы"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.name} - Skystore'
        context['page_cached'] = True
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """CBV для создания нового товара"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить товар - Skystore'
        return context


class ContactsTemplateView(TemplateView):
    """CBV для страницы контактов с обработкой формы"""
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты - Skystore'
        return context

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        print(f"Получено сообщение от {name} (тел: {phone}): {message}")

        context = self.get_context_data()
        context['success_message'] = 'Сообщение успешно отправлено!'
        return render(request, self.template_name, context)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """CBV для редактирования существующего товара"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def test_func(self):
        """Проверка прав на редактирование"""
        product = self.get_object()
        user = self.request.user

        # Владелец может редактировать
        if product.owner == user:
            return True

        # Модератор продуктов может редактировать
        if user.has_perm('catalog.change_product'):
            return True

        return False

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для редактирования этого продукта")

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование {self.object.name} - Skystore'
        return context


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """CBV для удаления товара"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')

    def test_func(self):
        """Проверка прав на удаление"""
        product = self.get_object()
        user = self.request.user

        # Владелец может удалять
        if product.owner == user:
            return True

        # Модератор продуктов может удалять (у него есть право delete_product)
        if user.has_perm('catalog.delete_product'):
            return True

        return False

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для удаления этого продукта")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление {self.object.name} - Skystore'
        return context


class ProductUnpublishView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """CBV для отмены публикации товара"""
    model = Product
    fields = ['is_published']
    template_name = 'catalog/product_unpublish.html'
    permission_required = 'catalog.can_unpublish_product'

    def form_valid(self, form):
        """Отменяем публикацию"""
        form.instance.is_published = False
        form.instance.publish_status = 'rejected'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})


class CategoryProductsView(ListView):
    """CBV для отображения продуктов в категории"""
    template_name = 'catalog/category_products.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """Получаем продукты категории через сервис"""
        category_id = self.kwargs['category_id']
        return ProductService.get_products_in_category(category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs['category_id']

        # Получаем информацию о категории
        category_data = ProductService.get_category_with_product_count(category_id)

        context.update(category_data)
        context['title'] = f'{context["category"].name} - Skystore'
        context['category_id'] = category_id
        context['cache_info'] = {
            'timestamp': category_data.get('timestamp'),
            'current_time': time.time()
        }

        return context
