from django.conf import settings
from django.db import models
from django.urls import reverse


class Plant(models.Model):
    class Status(models.TextChoices):
        HEALTHY = 'healthy', 'سالم'
        NEEDS_ATTENTION = 'needs_attention', 'نیازمند توجه'
        SICK = 'sick', 'بیمار'
        RECOVERING = 'recovering', 'در حال بهبود'
        DEAD = 'dead', 'از بین رفته'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='plants'
    )
    name = models.CharField(max_length=200)
    scientific_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='plants/', blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.HEALTHY
    )
    light_need = models.CharField(max_length=100, blank=True)
    temperature = models.CharField(max_length=50, blank=True)
    humidity = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plants:detail', kwargs={'pk': self.pk})

    @property
    def last_watering(self):
        return self.care_logs.filter(care_type__slug='watering').first()

    @property
    def next_watering(self):
        return self.schedules.filter(
            care_type__slug='watering',
            is_active=True
        ).first()

    def save(self, *args, **kwargs):
        """فشرده‌سازی خودکار تصویر"""
        if self.image and hasattr(self.image, 'file'):
            try:
                from PIL import Image
                from io import BytesIO
                from django.core.files.base import ContentFile

                img = Image.open(self.image)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                # resize اگر بزرگ‌تر از 1200px
                max_size = (1200, 1200)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                output = BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                output.seek(0)

                self.image = ContentFile(output.read(), name=self.image.name)
            except Exception:
                pass

        super().save(*args, **kwargs)


class PlantPhoto(models.Model):
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    image = models.ImageField(upload_to='plants/photos/')
    caption = models.CharField(max_length=255, blank=True)
    taken_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-taken_at']

    def __str__(self):
        return f"{self.plant.name} - {self.taken_at:%Y/%m/%d}"