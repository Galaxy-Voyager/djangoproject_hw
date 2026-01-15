from django.urls import path
from .views import (
    HomeListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ContactsTemplateView,
    ProductUnpublishView,
    CategoryProductsView
)
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('contacts/', ContactsTemplateView.as_view(), name='contacts'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('', views.HomeListView.as_view(), name='home'),
    path('contacts/', views.ContactsTemplateView.as_view(), name='contacts'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('product/<int:pk>/unpublish/',
         views.ProductUnpublishView.as_view(),
         name='product_unpublish'),
    path('category/<int:category_id>/products/',
         CategoryProductsView.as_view(),
         name='category_products'),
]
