import secrets
from django.db import models
from plants.models import Plant


def generate_token():
    return secrets.token_urlsafe(32)


class QRCode(models.Model):
    class QRType(models.TextChoices):
        PLANT = 'plant', 'Plant QR'
        ACTION = 'action', 'Action QR'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'فعال'
        REVOKED = 'revoked', 'غیرفعال'
        EXPIRED = 'expired', 'منقضی'

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='qr_codes'
    )
    qr_type = models.CharField(max_length=20, choices=QRType.choices)
    action_type = models.CharField(
        max_length=50,
        blank=True,
        help_text='برای Action QR: مثلاً watering'
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        default=generate_token,
        db_index=True
    )

    # ✅ فیلد جدید: تصویر QR
    image = models.ImageField(
        upload_to='qrcodes/',
        blank=True,
        null=True,
        help_text='تصویر PNG تولید شده از QR'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    expires_at = models.DateTimeField(blank=True, null=True)
    scan_count = models.PositiveIntegerField(default=0)
    last_scanned_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_qr_type_display()} - {self.plant.name}"

    @property
    def is_valid(self):
        if self.status != self.Status.ACTIVE:
            return False
        if self.expires_at:
            from django.utils import timezone
            if timezone.now() > self.expires_at:
                return False
        return True


class QRScanLog(models.Model):
    qr_code = models.ForeignKey(
        QRCode,
        on_delete=models.CASCADE,
        related_name='scan_logs'
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-scanned_at']