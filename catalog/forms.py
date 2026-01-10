import os
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from .models import Product, Category

# Константы для запрещенных слов
FORBIDDEN_WORDS = [
    'казино', 'криптовалюта', 'крипта', 'биржа',
    'дешево', 'бесплатно', 'обман', 'полиция', 'радар'
]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'category', 'price']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название товара'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Введите описание товара'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            })
        }
        labels = {
            'name': 'Название товара',
            'description': 'Описание',
            'image': 'Изображение',
            'category': 'Категория',
            'price': 'Цена'
        }

    def __init__(self, *args, **kwargs):
        # Получаем текущего пользователя из kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Дополнительная стилизация
        for field_name, field in self.fields.items():
            if field_name == 'category':
                field.empty_label = "Выберите категорию"
            if field_name == 'image':
                field.widget.attrs.update({
                    'accept': 'image/*',
                    'data-max-size': '5242880'  # 5 МБ в байтах
                })
                field.help_text = 'Максимальный размер: 5 МБ. Допустимые форматы: JPG, PNG, GIF, BMP, WebP'

    def clean_name(self):
        """Валидация названия товара на запрещенные слова"""
        name = self.cleaned_data['name'].lower()

        for forbidden_word in FORBIDDEN_WORDS:
            if forbidden_word in name:
                raise ValidationError(
                    f'Название содержит запрещенное слово: "{forbidden_word}". '
                    f'Пожалуйста, выберите другое название.'
                )

        return self.cleaned_data['name']

    def clean_description(self):
        """Валидация описания товара на запрещенные слова"""
        description = self.cleaned_data['description'].lower()

        for forbidden_word in FORBIDDEN_WORDS:
            if forbidden_word in description:
                raise ValidationError(
                    f'Описание содержит запрещенное слово: "{forbidden_word}". '
                    f'Пожалуйста, измените описание.'
                )

        return self.cleaned_data['description']

    def clean_price(self):
        """Кастомная валидация цены (не может быть отрицательной)"""
        price = self.cleaned_data['price']

        if price < 0:
            raise ValidationError(
                'Цена не может быть отрицательной. '
                'Пожалуйста, введите корректное значение.'
            )

        return price

    def clean_image(self):
        """Валидация загружаемого изображения"""
        image = self.cleaned_data.get('image')
        if not image:
            return image
        max_size = 5 * 1024 * 1024  # 5 МБ в байтах
        if image.size > max_size:
            raise ValidationError(
                f'Размер файла не должен превышать 5 МБ. '
                f'Текущий размер: {image.size / (1024 * 1024):.1f} МБ.'
            )
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        ext = os.path.splitext(image.name)[1].lower()

        if ext not in valid_extensions:
            raise ValidationError(
                f'Неподдерживаемый формат файла. '
                f'Допустимые форматы: {", ".join(valid_extensions)}'
            )
        if hasattr(image, 'content_type'):
            valid_mime_types = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
            if image.content_type not in valid_mime_types:
                raise ValidationError(
                    f'Неподдерживаемый тип файла. '
                    f'Файл должен быть изображением.'
                )

        return image

    def save(self, commit=True):
        """Переопределяем сохранение для автоматического назначения владельца"""
        instance = super().save(commit=False)

        if not instance.pk and self.user:
            instance.owner = self.user

        if commit:
            instance.save()

        return instance
