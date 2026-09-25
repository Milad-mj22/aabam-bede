from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from plants.models import Plant
from care.models import CareSchedule, CareLog
from .models import Notification
from .services import create_notification


@shared_task
def send_daily_reminders():
    """هر روز صبح یادآوری‌ها را ارسال کن"""
    from core.services import _get_schedules_for_day

    today = timezone.now().date()
    users_with_schedules = CareSchedule.objects.filter(
        is_active=True,
    ).values_list('plant__owner', flat=True).distinct()

    total = 0
    for user_id in users_with_schedules:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            continue

        schedules = _get_schedules_for_day(user, today)

        for task in schedules:
            # جلوگیری از تکرار
            exists = Notification.objects.filter(
                user=user,
                plant_id=task['plant_id'],
                notification_type='watering' if task['care_type_slug'] == 'watering' else 'reminder',
                created_at__date=today,
            ).exists()

            if exists:
                continue

            create_notification(
                user=user,
                title=f"{task['care_type_icon']} {task['care_type_name']} {task['plant_name']}",
                message=f"امروز نوبت {task['care_type_name']} گیاه «{task['plant_name']}» است.",
                notification_type=_map_care_type(task['care_type_slug']),
                priority='high' if task['care_type_slug'] == 'watering' else 'normal',
                plant_id=task['plant_id'],
                url=f"/plants/{task['plant_id']}/",
                icon=task['care_type_icon'],
            )
            total += 1

    return f'{total} یادآوری ارسال شد.'


@shared_task
def check_overdue_tasks():
    """بررسی کارهای عقب‌افتاده"""
    from core.services import _get_overdue_schedules

    today = timezone.now().date()
    users = Plant.objects.filter(is_active=True).values_list('owner', flat=True).distinct()

    total = 0
    for user_id in users:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            continue

        overdue = _get_overdue_schedules(user, today)

        # فقط عقب‌افتاده‌های بیش از ۲ روز
        serious = [t for t in overdue if t['days_overdue'] >= 2]

        if serious:
            create_notification(
                user=user,
                title=f"⚠️ {len(serious)} کار عقب‌افتاده",
                message=f"شما {len(serious)} فعالیت مراقبتی عقب‌افتاده دارید. لطفاً بررسی کنید.",
                notification_type='system',
                priority='urgent',
                url='/care/calendar/',
                icon='⚠️',
            )
            total += 1

    return f'{total} هشدار عقب‌افتادگی ارسال شد.'


@shared_task
def cleanup_old_notifications():
    """پاک‌سازی نوتیفیکیشن‌های قدیمی"""
    threshold = timezone.now() - timedelta(days=30)
    deleted, _ = Notification.objects.filter(
        is_read=True,
        read_at__lt=threshold,
    ).delete()
    return f'{deleted} نوتیفیکیشن قدیمی پاک شد.'


@shared_task
def send_email_notification(user_id, subject, message):
    """ارسال ایمیل اطلاع‌رسانی"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return 'کاربر یافت نشد.'

    if not user.email:
        return 'کاربر ایمیل ندارد.'

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
    return f'ایمیل به {user.email} ارسال شد.'


# ============================================================
#  Helper
# ============================================================
def _map_care_type(slug):
    mapping = {
        'watering': 'watering',
        'fertilizer': 'fertilizer',
        'medicine': 'medicine',
        'pest_control': 'pest_control',
    }
    return mapping.get(slug, 'reminder')