from datetime import date, timedelta
from django.db.models import Count, Q
from django.utils import timezone
from plants.models import Plant
from care.models import CareSchedule, CareLog, CareType


def get_dashboard_stats(user):
    """آمار کلی برای داشبورد"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    plants = Plant.objects.filter(owner=user, is_active=True)

    # آمار گیاهان
    stats = {
        'total_plants': plants.count(),
        'healthy_plants': plants.filter(status='healthy').count(),
        'need_attention': plants.filter(status='needs_attention').count(),
        'sick_plants': plants.filter(status='sick').count(),
        'recovering_plants': plants.filter(status='recovering').count(),
    }

    # فعالیت‌های امروز
    today_logs = CareLog.objects.filter(
        plant__owner=user,
        performed_at__date=today,
    )
    stats['today_activities'] = today_logs.count()

    # فعالیت‌های هفته گذشته (برای مقایسه)
    week_logs = CareLog.objects.filter(
        plant__owner=user,
        performed_at__date__gte=week_ago,
    ).count()
    stats['week_activities'] = week_logs

    # برنامه‌های امروز
    today_schedules = _get_schedules_for_day(user, today)
    stats['today_schedules'] = len(today_schedules)
    stats['done_today'] = today_logs.count()
    stats['pending_today'] = max(0, len(today_schedules) - today_logs.count())

    # برنامه‌های عقب‌افتاده
    overdue = _get_overdue_schedules(user, today)
    stats['overdue_tasks'] = len(overdue)

    # گیاهان نیازمند آبیاری امروز
    watering_today = [
        s for s in today_schedules if s['care_type_slug'] == 'watering'
    ]
    stats['need_watering'] = len(watering_today)

    return stats


def _get_schedules_for_day(user, target_date):
    """همه برنامه‌های فعال در یک روز خاص"""
    schedules = CareSchedule.objects.filter(
        plant__owner=user,
        is_active=True,
        start_date__lte=target_date,
    ).select_related('plant', 'care_type')

    result = []
    for sched in schedules:
        # بررسی بازه‌ی انقضا
        if sched.end_date and target_date > sched.end_date:
            continue

        delta = (target_date - sched.start_date).days
        if delta < 0:
            continue

        interval = max(sched.interval_days, 1)

        if sched.frequency == 'daily' and delta >= 0:
            match = True
        elif sched.frequency == 'weekly':
            match = (delta % 7 == 0)
        elif sched.frequency == 'monthly':
            # هر ۳۰ روز
            match = (delta % 30 == 0)
        elif sched.frequency == 'every_n_days':
            match = (delta % interval == 0)
        else:  # custom
            match = (delta % interval == 0)

        if match:
            result.append({
                'schedule_id': sched.pk,
                'plant_id': sched.plant_id,
                'plant_name': sched.plant.name,
                'plant_image': sched.plant.image.url if sched.plant.image else None,
                'care_type_name': sched.care_type.name,
                'care_type_slug': sched.care_type.slug,
                'care_type_icon': sched.care_type.icon or '✓',
                'care_type_color': sched.care_type.color or '#10b981',
                'time_of_day': sched.time_of_day,
            })

    # مرتب بر اساس ساعت
    result.sort(key=lambda x: (x['time_of_day'] is None, x['time_of_day']))
    return result


def _get_overdue_schedules(user, today):
    """برنامه‌هایی که از موعد گذشته و انجام نشده"""
    overdue = []
    # بررسی ۷ روز گذشته
    for day_offset in range(1, 8):
        check_date = today - timedelta(days=day_offset)
        day_schedules = _get_schedules_for_day(user, check_date)

        for s in day_schedules:
            # آیا لاگی برای این برنامه در آن روز ثبت شده؟
            exists = CareLog.objects.filter(
                plant_id=s['plant_id'],
                care_type__slug=s['care_type_slug'],
                performed_at__date=check_date,
            ).exists()

            if not exists:
                s['days_overdue'] = day_offset
                s['scheduled_date'] = check_date
                overdue.append(s)

    return overdue


def get_activity_chart_data(user, days=14):
    """داده‌های چارت فعالیت‌ها در N روز گذشته"""
    today = timezone.now().date()
    start = today - timedelta(days=days - 1)

    # همه لاگ‌ها
    logs = CareLog.objects.filter(
        plant__owner=user,
        performed_at__date__gte=start,
        performed_at__date__lte=today,
    ).values('performed_at__date', 'care_type__slug').annotate(
        count=Count('id')
    )

    # گروه‌بندی
    data_by_date = {}
    for item in logs:
        d = item['performed_at__date']
        slug = item['care_type__slug']
        data_by_date.setdefault(d, {})
        data_by_date[d][slug] = item['count']

    # ساخت آرایه‌ها
    labels = []
    datasets_data = {
        'watering': [],
        'fertilizer': [],
        'medicine': [],
        'other': [],
    }

    for i in range(days):
        d = start + timedelta(days=i)
        labels.append(d.strftime('%m/%d'))
        day_data = data_by_date.get(d, {})

        datasets_data['watering'].append(day_data.get('watering', 0))
        datasets_data['fertilizer'].append(day_data.get('fertilizer', 0))
        datasets_data['medicine'].append(day_data.get('medicine', 0))

        other_count = sum(
            v for k, v in day_data.items()
            if k not in ('watering', 'fertilizer', 'medicine')
        )
        datasets_data['other'].append(other_count)

    return {
        'labels': labels,
        'watering': datasets_data['watering'],
        'fertilizer': datasets_data['fertilizer'],
        'medicine': datasets_data['medicine'],
        'other': datasets_data['other'],
    }


def get_plant_status_chart(user):
    """داده‌های چارت دایره‌ای وضعیت گیاهان"""
    plants = Plant.objects.filter(owner=user, is_active=True)

    data = {
        'healthy': plants.filter(status='healthy').count(),
        'needs_attention': plants.filter(status='needs_attention').count(),
        'sick': plants.filter(status='sick').count(),
        'recovering': plants.filter(status='recovering').count(),
    }

    return {
        'labels': ['سالم', 'نیازمند توجه', 'بیمار', 'در حال بهبود'],
        'values': list(data.values()),
        'colors': ['#22c55e', '#f59e0b', '#ef4444', '#06b6d4'],
    }


def get_care_type_distribution(user, days=30):
    """توزیع انواع فعالیت در N روز گذشته"""
    start = timezone.now().date() - timedelta(days=days)

    logs = CareLog.objects.filter(
        plant__owner=user,
        performed_at__date__gte=start,
    ).values('care_type__name', 'care_type__icon', 'care_type__color').annotate(
        count=Count('id')
    ).order_by('-count')[:6]

    return {
        'labels': [f"{item['care_type__icon'] or ''} {item['care_type__name']}" for item in logs],
        'values': [item['count'] for item in logs],
        'colors': [item['care_type__color'] or '#10b981' for item in logs],
    }