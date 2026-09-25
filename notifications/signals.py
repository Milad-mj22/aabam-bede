from django.db.models.signals import post_save
from django.dispatch import receiver
from care.models import CareLog
from qrcodes.models import QRScanLog
from .services import notify_qr_scan


@receiver(post_save, sender=QRScanLog)
def on_qr_scan(sender, instance, created, **kwargs):
    """وقتی QR اسکن می‌شود، به مالک اطلاع بده"""
    if not created:
        return

    qr = instance.qr_code
    plant = qr.plant

    # فقط برای اسکن‌های موفق و برای Plant QR
    # (برای Action QR، لاگ فعالیت کافی است)
    if instance.success and qr.qr_type == qr.QRType.PLANT:
        notify_qr_scan(plant, instance)