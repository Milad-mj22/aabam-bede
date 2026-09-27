from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Status(models.TextChoices):
        PENDING = 'pending', 'در انتظار تأیید'
        ACTIVE = 'active', 'فعال'
        REJECTED = 'rejected', 'رد شده'
        SUSPENDED = 'suspended', 'معلق'

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def is_active_user(self):
        return True
        return self.status == self.Status.ACTIVE