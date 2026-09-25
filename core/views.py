from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from plants.models import Plant
from care.models import CareLog
from .services import (
    get_dashboard_stats,
    _get_schedules_for_day,
    _get_overdue_schedules,
    get_activity_chart_data,
    get_plant_status_chart,
    get_care_type_distribution,
)


@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    # آمار کلی
    stats = get_dashboard_stats(user)

    # برنامه‌های امروز
    today_schedules = _get_schedules_for_day(user, today)

    # برنامه‌های عقب‌افتاده
    overdue_tasks = _get_overdue_schedules(user, today)

    # گیاهان اخیر
    recent_plants = Plant.objects.filter(
        owner=user, is_active=True
    ).order_by('-created_at')[:6]

    # فعالیت‌های اخیر
    recent_logs = CareLog.objects.filter(
        plant__owner=user
    ).select_related('plant', 'care_type').order_by('-performed_at')[:8]

    context = {
        'stats': stats,
        'today_schedules': today_schedules,
        'overdue_tasks': overdue_tasks[:5],
        'recent_plants': recent_plants,
        'recent_logs': recent_logs,
        'today': today,
    }
    return render(request, 'core/dashboard.html', context)


# ============================================================
#  AJAX endpoints
# ============================================================

@login_required
def dashboard_charts(request):
    """داده‌های چارت‌ها به‌صورت JSON"""
    user = request.user

    return JsonResponse({
        'activity': get_activity_chart_data(user, days=14),
        'plant_status': get_plant_status_chart(user),
        'care_distribution': get_care_type_distribution(user, days=30),
    })








from django.shortcuts import render, redirect
from django.urls import reverse


def landing(request):
    """صفحه لندینگ عمومی"""
    # اگر کاربر لاگین است، مستقیم به داشبورد برود
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    context = {
        'features': [
            {
                'icon': 'bi-droplet-fill',
                'title': 'یادآوری هوشمند آبیاری',
                'description': 'هر وقت گیاهت تشنه شد، بهت خبر می‌دیم. دیگه یادت نمی‌ره!',
                'color': '#0ea5e9',
            },
            {
                'icon': 'bi-qr-code',
                'title': 'QR Code اختصاصی',
                'description': 'برای هر گیاه یک QR بساز، روی گلدون بچسبون، با موبایل اسکن کن!',
                'color': '#10b981',
            },
            {
                'icon': 'bi-calendar-check',
                'title': 'تقویم مراقبت',
                'description': 'برنامه آبیاری، کوددهی، دارو و هر فعالیتی رو زمان‌بندی کن.',
                'color': '#f59e0b',
            },
            {
                'icon': 'bi-graph-up-arrow',
                'title': 'تاریخچه کامل',
                'description': 'همه فعالیت‌های گیاهت در یک تایم‌لاین زیبا ثبت می‌شه.',
                'color': '#8b5cf6',
            },
            {
                'icon': 'bi-images',
                'title': 'آلبوم رشد',
                'description': 'عکس‌های گیاهت رو در طول زمان ذخیره کن و رشدش رو ببین.',
                'color': '#ec4899',
            },
            {
                'icon': 'bi-bell-fill',
                'title': 'اطلاع‌رسانی هوشمند',
                'description': 'از طریق مرورگر، ایمیل یا داخل اپ، همیشه در جریان باش.',
                'color': '#ef4444',
            },
        ],
        'steps': [
            {
                'number': '1',
                'title': 'ثبت‌نام کن',
                'description': 'در چند ثانیه حساب بساز، رایگان!',
                'icon': 'bi-person-plus',
            },
            {
                'number': '2',
                'title': 'گیاهت رو اضافه کن',
                'description': 'اسم، عکس و مشخصات گیاهت رو وارد کن.',
                'icon': 'bi-flower1',
            },
            {
                'number': '3',
                'title': 'برنامه بساز',
                'description': 'بگو کی آب بدی، کی کود بدی، کی دارو.',
                'icon': 'bi-calendar-plus',
            },
            {
                'number': '4',
                'title': 'QR بچسبون',
                'description': 'QR رو پرینت کن، بچسبون روی گلدون، خلاص!',
                'icon': 'bi-qr-code-scan',
            },
        ],
        'faqs': [
            {
                'question': '«آبم بده» رایگانه؟',
                'answer': 'بله! برای همیشه رایگان. امکانات پیشرفته هم به‌زودی اضافه می‌شه.',
            },
            {
                'question': 'چند تا گیاه می‌تونم اضافه کنم؟',
                'answer': 'بدون محدودیت! هرچقدر گیاه داری، همون‌قدر می‌تونی ثبت کنی.',
            },
            {
                'question': 'QR Code چطور کار می‌کنه؟',
                'answer': 'برای هر گیاه یک QR اختصاصی ساخته می‌شه. چاپش کن، روی گلدون بچسبون. با موبایل اسکن کن تا اطلاعات و تاریخچه گیاه رو ببینی یا سریع فعالیت ثبت کنی.',
            },
            {
                'question': 'بدون اینترنت هم کار می‌کنه؟',
                'answer': 'برای دیدن اطلاعات، بله نیاز به اینترنت داری. اما نگران نباش، اپ روی موبایل هم به‌خوبی کار می‌کنه.',
            },
            {
                'question': 'اطلاعاتم امن هست؟',
                'answer': 'قطعاً! اطلاعات گیاهانت رمزنگاری شده و فقط خودت بهشون دسترسی داری.',
            },
            {
                'question': 'اپ موبایل هم دارید؟',
                'answer': 'نسخه وب روی موبایل عالی کار می‌کنه. اپ اختصاصی iOS/Android هم به‌زودی.',
            },
        ],
    }
    return render(request, 'landing/index.html', context)