from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    class Type(models.TextChoices):
        WATERING = 'watering', 'آبیاری'
        FERTILIZER = 'fertilizer', 'کوددهی'
        MEDICINE = 'medicine', 'دارو'
        PEST_CONTROL = 'pest_control', 'سم‌پاشی'
        REMINDER = 'reminder', 'یادآوری عمومی'
        SYSTEM = 'system', 'سیستمی'
        QR_SCAN = 'qr_scan', 'اسکن QR'

    class Priority(models.TextChoices):
        LOW = 'low', 'کم'
        NORMAL = 'normal', 'معمولی'
        HIGH = 'high', 'بالا'
        URGENT = 'urgent', 'فوری'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    plant = models.ForeignKey(
        'plants.Plant',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.REMINDER
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL
    )
    url = models.CharField(max_length=500, blank=True)
    icon = models.CharField(max_length=20, blank=True, default='🔔')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.title}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    @property
    def priority_color(self):
        return {
            'low': '#64748b',
            'normal': '#06b6d4',
            'high': '#f59e0b',
            'urgent': '#ef4444',
        }.get(self.priority, '#06b6d4')

    @property
    def time_ago(self):
        """نمایش نسبی زمان"""
        delta = timezone.now() - self.created_at
        seconds = delta.total_seconds()

        if seconds < 60:
            return 'همین الان'
        elif seconds < 3600:
            return f'{int(seconds // 60)} دقیقه پیش'
        elif seconds < 86400:
            return f'{int(seconds // 3600)} ساعت پیش'
        elif seconds < 604800:
            return f'{int(seconds // 86400)} روز پیش'
        else:
            return self.created_at.strftime('%Y/%m/%d')