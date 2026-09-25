from django.db import models

# Create your models here.
from django.db import models


class SystemSetting(models.Model):
    class RegistrationMode(models.TextChoices):
        AUTO = 'auto', 'فعال‌سازی خودکار'
        APPROVAL = 'approval', 'نیازمند تأیید مدیر'
        CLOSED = 'closed', 'ثبت‌نام بسته'

    registration_mode = models.CharField(
        max_length=20,
        choices=RegistrationMode.choices,
        default=RegistrationMode.APPROVAL
    )
    allow_registration = models.BooleanField(default=True)
    enable_plant_qr = models.BooleanField(default=True)
    enable_action_qr = models.BooleanField(default=True)
    qr_expiration_days = models.PositiveIntegerField(default=0, help_text='0 = بدون انقضا')
    enable_email_notifications = models.BooleanField(default=False)
    enable_browser_notifications = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تنظیمات سیستم'
        verbose_name_plural = 'تنظیمات سیستم'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AuditLog(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(max_length=200)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']