from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify
from plants.models import Plant


class CareType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='مثلاً: 💧')
    color = models.CharField(max_length=20, blank=True, default='#0d6efd')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CareSchedule(models.Model):
    class Frequency(models.TextChoices):
        DAILY = 'daily', 'روزانه'
        EVERY_N_DAYS = 'every_n_days', 'هر N روز'
        WEEKLY = 'weekly', 'هفتگی'
        MONTHLY = 'monthly', 'ماهانه'
        CUSTOM = 'custom', 'سفارشی'

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    care_type = models.ForeignKey(CareType, on_delete=models.PROTECT)
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.EVERY_N_DAYS
    )
    interval_days = models.PositiveIntegerField(default=1)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    time_of_day = models.TimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.plant.name} - {self.care_type.name}"


class CareLog(models.Model):
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='care_logs'
    )
    care_type = models.ForeignKey(CareType, on_delete=models.PROTECT)
    schedule = models.ForeignKey(
        CareSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    performed_at = models.DateTimeField()
    amount = models.CharField(max_length=100, blank=True)
    product = models.CharField(max_length=200, blank=True)
    note = models.TextField(blank=True)
    image = models.ImageField(upload_to='care_logs/', blank=True, null=True)

    # متادیتای امنیتی برای Action QR
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True)
    source = models.CharField(max_length=20, default='web')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.plant.name} - {self.care_type.name} @ {self.performed_at}"