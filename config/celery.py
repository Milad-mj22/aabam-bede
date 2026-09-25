import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('plantcare')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# ============================================================
#  Scheduled Tasks
# ============================================================
app.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'notifications.tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),   # ۸ صبح هر روز
    },
    'check-overdue-tasks': {
        'task': 'notifications.tasks.check_overdue_tasks',
        'schedule': crontab(hour=20, minute=0),  # ۸ شب هر روز
    },
    'cleanup-old-notifications': {
        'task': 'notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # یکشنبه‌ها ۳ صبح
    },
}

app.conf.timezone = 'Asia/Tehran'