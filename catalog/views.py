from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from .models import Product, Category
from .forms import ProductForm


class HomeListView(ListView):
    """CBV для главной страницы с пагинацией"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 6
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Skystore - Главная'
        return context


class ProductDetailView(DetailView):
    """CBV для детальной страницы товара"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.name} - Skystore'
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
