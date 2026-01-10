from django import forms
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'preview', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок статьи'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Введите содержимое статьи'
            }),
            'preview': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержимое',
            'preview': 'Превью',
            'is_published': 'Опубликовать сразу'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Дополнительная настройка полей
        if self.user and not self.user.groups.filter(name='Контент-менеджер').exists():
            self.fields['is_published'].widget = forms.HiddenInput()
            self.fields['is_published'].initial = False

    def save(self, commit=True):
        """Переопределяем сохранение для автоматического назначения владельца"""
        instance = super().save(commit=False)
        if not instance.pk and self.user:
            instance.owner = self.user
        if self.user and not self.user.groups.filter(name='Контент-менеджер').exists():
            instance.is_published = False

        if commit:
            instance.save()

        return instance
