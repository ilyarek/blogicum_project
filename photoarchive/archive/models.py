from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import uuid

def document_upload_path(instance, filename):
    """Генерирует путь для загрузки документов"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"documents/{filename}"

def thumbnail_upload_path(instance, filename):
    """Генерирует путь для миниатюр"""
    ext = filename.split('.')[-1]
    filename = f"thumb_{uuid.uuid4()}.{ext}"
    return f"thumbnails/{filename}"

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('photo', 'Фотография'),
        ('scan', 'Скан документа'),
        ('multipage', 'Многостраничный документ'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    original_date = models.DateField(verbose_name="Дата оригинального документа")
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    document_file = models.FileField(
        upload_to=document_upload_path,
        verbose_name="Файл документа"
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        default='photo',
        verbose_name="Тип документа"
    )
    thumbnail = models.ImageField(
        upload_to=thumbnail_upload_path,
        blank=True,
        null=True,
        verbose_name="Миниатюра"
    )
    keywords = models.TextField(
        blank=True,
        verbose_name="Ключевые слова (через запятую)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    
    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ['-upload_date']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Создание миниатюры при сохранении"""
        if self.document_file and not self.thumbnail:
            self.create_thumbnail()
        super().save(*args, **kwargs)
    
    def create_thumbnail(self):
        """Создает миниатюру для изображения"""
        try:
            if self.document_file and self.document_file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                from PIL import Image
                from io import BytesIO
                from django.core.files.base import ContentFile
                import os
                
                # Открываем изображение
                image = Image.open(self.document_file)
                
                # Конвертируем в RGB если нужно
                if image.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGB')
                    else:
                        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                        image = background
                
                # Создаем миниатюру
                image.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                # Сохраняем в память
                thumb_io = BytesIO()
                image.save(thumb_io, format='JPEG', quality=85)
                
                # Создаем имя файла для миниатюры
                filename = os.path.basename(self.document_file.name)
                name, ext = os.path.splitext(filename)
                thumb_filename = f'thumb_{name}.jpg'
                
                # Сохраняем миниатюру
                self.thumbnail.save(
                    thumb_filename,
                    ContentFile(thumb_io.getvalue()),
                    save=False
                )
                thumb_io.close()
                
        except Exception as e:
            print(f"Ошибка создания миниатюры для {self.document_file.name}: {e}")
            # Не устанавливаем миниатюру в случае ошибки
    
    def get_absolute_url(self):
        return reverse('document_detail', kwargs={'pk': self.pk})
    
    def get_keywords_list(self):
        """Возвращает список ключевых слов"""
        if self.keywords:
            return [kw.strip() for kw in self.keywords.split(',')]
        return []
    
    def can_be_downloaded(self):
        """Проверяет, можно ли скачать документ"""
        return self.is_active and self.document_file

class SearchLog(models.Model):
    """Лог поисковых запросов"""
    query = models.CharField(max_length=500, verbose_name="Поисковый запрос")
    date_from = models.DateField(null=True, blank=True, verbose_name="Дата с")
    date_to = models.DateField(null=True, blank=True, verbose_name="Дата по")
    search_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата поиска")
    results_count = models.IntegerField(default=0, verbose_name="Количество результатов")
    
    class Meta:
        verbose_name = "Лог поиска"
        verbose_name_plural = "Логи поиска"
        ordering = ['-search_date']