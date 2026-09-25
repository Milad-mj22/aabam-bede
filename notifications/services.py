from django.utils import timezone
from datetime import timedelta
from .models import Notification


def create_notification(
    user,
    title,
    message,
    notification_type=Notification.Type.REMINDER,
    priority=Notification.Priority.NORMAL,
    plant=None,
    url='',
    icon='🔔',
):
    """ساخت یک نوتیفیکیشن"""
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        plant=plant,
        url=url,
        icon=icon,
    )


def notify_watering_needed(plant, days=0):
    """یادآوری آبیاری"""
    if days == 0:
        title = f'💧 آبیاری {plant.name} امروز'
        message = f'گیاه «{plant.name}» امروز نیاز به آبیاری دارد.'
    else:
        title = f'💧 آبیاری {plant.name} نزدیک است'
        message = f'گیاه «{plant.name}» تا {days} روز دیگر نیاز به آبیاری دارد.'

    return create_notification(
        user=plant.owner,
        title=title,
        message=message,
        notification_type=Notification.Type.WATERING,
        priority=Notification.Priority.HIGH if days == 0 else Notification.Priority.NORMAL,
        plant=plant,
        url=f'/plants/{plant.pk}/',
        icon='💧',
    )


def notify_fertilizer_needed(plant, days=0):
    """یادآوری کوددهی"""
    title = f'🌱 زمان کوددهی {plant.name}'
    message = f'گیاه «{plant.name}» نیاز به کوددهی دارد.'

    return create_notification(
        user=plant.owner,
        title=title,
        message=message,
        notification_type=Notification.Type.FERTILIZER,
        priority=Notification.Priority.NORMAL,
        plant=plant,
        url=f'/plants/{plant.pk}/',
        icon='🌱',
    )


def notify_medicine_needed(plant, days=0):
    """یادآوری دارو"""
    title = f'💊 زمان مصرف دارو برای {plant.name}'
    message = f'گیاه «{plant.name}» نیاز به مصرف دارو دارد.'

    return create_notification(
        user=plant.owner,
        title=title,
        message=message,
        notification_type=Notification.Type.MEDICINE,
        priority=Notification.Priority.HIGH,
        plant=plant,
        url=f'/plants/{plant.pk}/',
        icon='💊',
    )


def notify_qr_scan(plant, scan_log=None):
    """اطلاع اسکن QR"""
    title = f'📱 QR گیاه «{plant.name}» اسکن شد'
    message = f'یک QR مربوط به گیاه «{plant.name}» اسکن شده است.'

    return create_notification(
        user=plant.owner,
        title=title,
        message=message,
        notification_type=Notification.Type.QR_SCAN,
        priority=Notification.Priority.LOW,
        plant=plant,
        url=f'/plants/{plant.pk}/#tab-qr',
        icon='📱',
    )


def mark_all_read(user):
    """علامت‌گذاری همه به‌عنوان خوانده‌شده"""
    return Notification.objects.filter(
        user=user,
        is_read=False,
    ).update(
        is_read=True,
        read_at=timezone.now(),
    )


def get_unread_count(user):
    """تعداد خوانده‌نشده‌ها"""
    return Notification.objects.filter(user=user, is_read=False).count()


def cleanup_old_notifications(days=30):
    """پاک‌سازی نوتیفیکیشن‌های قدیمی خوانده‌شده"""
    threshold = timezone.now() - timedelta(days=days)
    return Notification.objects.filter(
        is_read=True,
        read_at__lt=threshold,
    ).delete()