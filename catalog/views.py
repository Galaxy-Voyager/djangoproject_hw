from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from .forms import ProductForm


def home(request):
    """Контроллер главной страницы с пагинацией"""
    products_list = Product.objects.all().order_by('-created_at')

    # Пагинация - 6 товаров на страницу
    paginator = Paginator(products_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'Skystore - Главная'
    }
    return render(request, 'catalog/home.html', context)


def contacts(request):
    return render(request, 'catalog/contacts.html')


def product_detail(request, pk):
    """Контроллер для отображения детальной страницы товара"""
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
        'title': f'{product.name} - Skystore'
    }
    return render(request, 'catalog/product_detail.html', context)


def product_create(request):
    """Контроллер для создания нового товара"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            return redirect('catalog:product_detail', pk=product.pk)
    else:
        form = ProductForm()

    context = {
        'form': form,
        'title': 'Добавить товар - Skystore'
    }
    return render(request, 'catalog/product_form.html', context)
