from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import BlogPost
from .forms import BlogPostForm


class BlogPostListView(ListView):
    """CBV для списка статей блога"""
    model = BlogPost
    template_name = 'blog/blogpost_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        """Показываем только опубликованные статьи всем пользователям"""
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Блог - Skystore'
        return context


class BlogPostDetailView(DetailView):
    """CBV для детальной страницы статьи"""
    model = BlogPost
    template_name = 'blog/blogpost_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        """Увеличиваем счетчик просмотров"""
        obj = super().get_object(queryset)
        if self.request.user != obj.owner:
            obj.views_count += 1
            obj.save(update_fields=['views_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.title} - Блог Skystore'
        return context


class BlogPostCreateView(LoginRequiredMixin, CreateView):
    """CBV для создания новой статьи"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Новая статья - Блог Skystore'
        return context


class BlogPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """CBV для редактирования статьи"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'

    def test_func(self):
        """Проверка прав на редактирование"""
        post = self.get_object()
        user = self.request.user

        # Владелец может редактировать свою статью
        if post.owner == user:
            return True

        # Контент-менеджер может редактировать любые статьи
        if user.groups.filter(name='Контент-менеджер').exists():
            return True

        # Пользователь с явным правом can_manage_blog
        if user.has_perm('blog.can_manage_blog'):
            return True

        return False

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для редактирования этой статьи")

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование: {self.object.title}'
        return context


class BlogPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """CBV для удаления статьи"""
    model = BlogPost
    template_name = 'blog/blogpost_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')

    def test_func(self):
        """Проверка прав на удаление"""
        post = self.get_object()
        user = self.request.user

        # Владелец может удалять свою статью
        if post.owner == user:
            return True

        # Контент-менеджер может удалять любые статьи
        if user.groups.filter(name='Контент-менеджер').exists():
            return True

        # Пользователь с явным правом can_manage_blog
        if user.has_perm('blog.can_manage_blog'):
            return True

        return False

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для удаления этой статьи")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление: {self.object.title}'
        return context
