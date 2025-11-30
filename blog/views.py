from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import BlogPost
from .forms import BlogPostForm


class BlogPostListView(ListView):
    """Список блоговых записей"""
    model = BlogPost
    template_name = 'blog/blogpost_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        # Выводим только опубликованные записи
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')


class BlogPostDetailView(DetailView):
    """Детальная страница блоговой записи"""
    model = BlogPost
    template_name = 'blog/blogpost_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        # Получаем объект и увеличиваем счетчик просмотров
        obj = super().get_object(queryset=queryset)
        obj.views_count += 1
        obj.save()
        return obj


class BlogPostCreateView(CreateView):
    """Создание новой блоговой записи"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'
    success_url = reverse_lazy('blog:post_list')


class BlogPostUpdateView(UpdateView):
    """Редактирование блоговой записи"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'

    def get_success_url(self):
        # Перенаправляем на просмотр отредактированной статьи
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})


class BlogPostDeleteView(DeleteView):
    """Удаление блоговой записи"""
    model = BlogPost
    template_name = 'blog/blogpost_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')
