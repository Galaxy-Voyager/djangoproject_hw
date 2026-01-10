from django.db import models
from django.conf import settings


class BlogPost(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    content = models.TextField(
        verbose_name='Содержимое'
    )
    preview = models.ImageField(
        upload_to='blog/',
        verbose_name='Превью',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовано'
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество просмотров'
    )

    # Новое поле для домашки
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name='Автор',
        blank=True,
        null=True,
        related_name='blog_posts'
    )

    class Meta:
        verbose_name = 'Блоговая запись'
        verbose_name_plural = 'Блоговые записи'
        ordering = ['-created_at']
        permissions = [
            ('can_manage_blog', 'Может управлять блогом'),
        ]

    def __str__(self):
        return self.title


class BlogModeration(models.Model):
    """Модель для отслеживания модерации статей"""
    post = models.OneToOneField(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='moderation',
        verbose_name='Статья'
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Модератор'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'На модерации'),
            ('approved', 'Одобрено'),
            ('rejected', 'Отклонено'),
            ('needs_work', 'Требует доработки'),
        ],
        default='pending',
        verbose_name='Статус модерации'
    )
    comment = models.TextField(
        verbose_name='Комментарий модератора',
        blank=True
    )
    moderated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата модерации'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Модерация статьи'
        verbose_name_plural = 'Модерации статей'
        ordering = ['-moderated_at']

    def __str__(self):
        return f'Модерация: {self.post.title}'
