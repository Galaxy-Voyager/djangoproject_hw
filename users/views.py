from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterView(CreateView):
    """Контроллер регистрации пользователя"""
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """Переопределяем для отправки приветственного письма"""
        response = super().form_valid(form)
        user = form.instance

        # Отправка приветственного письма (в консоль для тестов)
        try:
            send_mail(
                subject='Добро пожаловать в Skystore!',
                message=f'''Здравствуйте, {user.first_name or 'Пользователь'}!

Добро пожаловать в Skystore - ваш личный магазин плагинов и кода!

Ваш аккаунт успешно создан.
Email для входа: {user.email}

С уважением,
Команда Skystore''',
                from_email='noreply@skystore.local',
                recipient_list=[user.email],
                fail_silently=True,  # Не падать при ошибке
            )
            messages.success(self.request, 'Регистрация успешна! Проверьте вашу почту.')
        except Exception:
            messages.success(self.request, 'Регистрация успешна!')

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация - Skystore'
        return context


class UserLoginView(LoginView):
    """Контроллер авторизации пользователя"""
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход - Skystore'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Добро пожаловать, {form.get_user().first_name or form.get_user().email}!')
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    """Контроллер выхода из системы"""

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)
