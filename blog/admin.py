from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_published', 'views_count', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content', 'owner__email')
    list_editable = ('is_published',)
    readonly_fields = ('views_count', 'created_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content', 'preview', 'owner')
        }),
        ('Статус и статистика', {
            'fields': ('is_published', 'views_count', 'created_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        """Автоматически назначаем владельца при создании через админку"""
        if not obj.pk:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
