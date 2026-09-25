from datetime import timedelta
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.db.models import Count
from plants.models import Plant
from care.models import CareLog, CareType
from core.models import SystemSetting, AuditLog
from .models import QRCode, QRScanLog
from .services import generate_qr_image, build_plant_qr_url, build_action_qr_url


# ============================================================
#  Helpers
# ============================================================

def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _log_scan(qr, request, success=True, note=''):
    QRScanLog.objects.create(
        qr_code=qr,
        ip_address=_get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        success=success,
        note=note,
    )


def _is_rate_limited(qr, request, seconds=30):
    """جلوگیری از اسکن تکراری از یک IP در بازه کوتاه"""
    ip = _get_client_ip(request)
    threshold = timezone.now() - timedelta(seconds=seconds)
    return QRScanLog.objects.filter(
        qr_code=qr,
        ip_address=ip,
        scanned_at__gte=threshold,
    ).exists()


def _activate_qr_if_needed(qr):
    """اگر QR منقضی شده، وضعیت را به‌روز کن"""
    if qr.expires_at and timezone.now() > qr.expires_at and qr.status == QRCode.Status.ACTIVE:
        qr.status = QRCode.Status.EXPIRED
        qr.save(update_fields=['status'])


# ============================================================
#  Generate QR (login required)
# ============================================================

@login_required
def generate_plant_qr(request, plant_pk):
    settings_obj = SystemSetting.get_settings()
    if not settings_obj.enable_plant_qr:
        messages.error(request, 'تولید Plant QR غیرفعال است.')
        return redirect('plants:detail', pk=plant_pk)

    plant = get_object_or_404(Plant, pk=plant_pk, owner=request.user)

    # اگر QR فعالی وجود دارد، همان را برگردان
    existing = plant.qr_codes.filter(
        qr_type=QRCode.QRType.PLANT,
        status=QRCode.Status.ACTIVE,
    ).first()
    if existing:
        messages.info(request, 'یک QR فعال برای این گیاه وجود دارد.')
        return redirect('plants:detail', pk=plant.pk)

    qr = QRCode.objects.create(plant=plant, qr_type=QRCode.QRType.PLANT)

    if settings_obj.qr_expiration_days > 0:
        qr.expires_at = timezone.now() + timedelta(days=settings_obj.qr_expiration_days)

    url = build_plant_qr_url(request, qr.token)
    qr.image.save(
        f'plant_{plant.pk}_{qr.token[:8]}.png',
        generate_qr_image(url),
        save=True,
    )

    AuditLog.objects.create(
        user=request.user,
        action='generate_plant_qr',
        model_name='QRCode',
        object_id=str(qr.pk),
        ip_address=_get_client_ip(request),
    )

    messages.success(request, 'QR Code گیاه با موفقیت تولید شد.')
    return redirect('plants:detail', pk=plant.pk)


@login_required
def generate_action_qr(request, plant_pk, action):
    settings_obj = SystemSetting.get_settings()
    if not settings_obj.enable_action_qr:
        messages.error(request, 'تولید Action QR غیرفعال است.')
        return redirect('plants:detail', pk=plant_pk)

    plant = get_object_or_404(Plant, pk=plant_pk, owner=request.user)

    # بررسی معتبر بودن action
    if not CareType.objects.filter(slug=action, is_active=True).exists():
        messages.error(request, 'نوع فعالیت نامعتبر است.')
        return redirect('plants:detail', pk=plant.pk)

    # بررسی وجود QR فعال برای همان action
    existing = plant.qr_codes.filter(
        qr_type=QRCode.QRType.ACTION,
        action_type=action,
        status=QRCode.Status.ACTIVE,
    ).first()
    if existing:
        messages.info(request, f'یک QR فعال برای «{action}» وجود دارد.')
        return redirect('plants:detail', pk=plant.pk)

    qr = QRCode.objects.create(
        plant=plant,
        qr_type=QRCode.QRType.ACTION,
        action_type=action,
    )

    if settings_obj.qr_expiration_days > 0:
        qr.expires_at = timezone.now() + timedelta(days=settings_obj.qr_expiration_days)

    url = build_action_qr_url(request, qr.token)
    qr.image.save(
        f'action_{action}_{plant.pk}_{qr.token[:8]}.png',
        generate_qr_image(url),
        save=True,
    )

    AuditLog.objects.create(
        user=request.user,
        action='generate_action_qr',
        model_name='QRCode',
        object_id=str(qr.pk),
        metadata={'action': action},
        ip_address=_get_client_ip(request),
    )

    messages.success(request, f'QR عملیات «{action}» تولید شد.')
    return redirect('plants:detail', pk=plant.pk)


@login_required
@require_POST
def revoke_qr(request, qr_pk):
    qr = get_object_or_404(QRCode, pk=qr_pk, plant__owner=request.user)
    qr.status = QRCode.Status.REVOKED
    qr.save(update_fields=['status'])

    AuditLog.objects.create(
        user=request.user,
        action='revoke_qr',
        model_name='QRCode',
        object_id=str(qr.pk),
        ip_address=_get_client_ip(request),
    )

    messages.warning(request, 'QR غیرفعال شد.')
    return redirect('plants:detail', pk=qr.plant.pk)


# ============================================================
#  Public Plant Page (no login)
# ============================================================

@never_cache
def public_plant(request, token):
    qr = get_object_or_404(QRCode, token=token, qr_type=QRCode.QRType.PLANT)
    _activate_qr_if_needed(qr)

    if not qr.is_valid:
        _log_scan(qr, request, success=False, note='invalid status')
        return render(request, 'qrcodes/invalid.html', {
            'reason': qr.get_status_display(),
            'qr': qr,
        }, status=410)

    # به‌روزرسانی آمار
    qr.scan_count += 1
    qr.last_scanned_at = timezone.now()
    qr.save(update_fields=['scan_count', 'last_scanned_at'])
    _log_scan(qr, request)

    plant = qr.plant
    now = timezone.now()

    # آخرین لاگ‌ها
    recent_logs = plant.care_logs.select_related('care_type').all()[:15]

    # آمار خلاصه
    last_watering = plant.care_logs.filter(
        care_type__slug='watering'
    ).select_related('care_type').first()

    next_schedule = plant.schedules.filter(
        is_active=True,
        start_date__gte=now.date(),
    ).select_related('care_type').order_by('start_date').first()

    # فعالیت‌های امروز
    today_logs_count = plant.care_logs.filter(
        performed_at__date=now.date()
    ).count()

    return render(request, 'qrcodes/public_plant.html', {
        'plant': plant,
        'qr': qr,
        'recent_logs': recent_logs,
        'last_watering': last_watering,
        'next_schedule': next_schedule,
        'today_logs_count': today_logs_count,
        'now': now,
    })


# ============================================================
#  Action QR (no login)
# ============================================================

@never_cache
def action_qr(request, token):
    qr = get_object_or_404(QRCode, token=token, qr_type=QRCode.QRType.ACTION)
    _activate_qr_if_needed(qr)

    if not qr.is_valid:
        _log_scan(qr, request, success=False, note='invalid status')
        return render(request, 'qrcodes/invalid.html', {
            'reason': qr.get_status_display(),
            'qr': qr,
        }, status=410)

    plant = qr.plant
    ip = _get_client_ip(request)

    # ⛔ Rate Limit: اگر در 30 ثانیه گذشته از همین IP اسکن شده
    if _is_rate_limited(qr, request, seconds=30):
        _log_scan(qr, request, success=False, note='rate limited')
        return render(request, 'qrcodes/action_already.html', {
            'plant': plant,
            'qr': qr,
            'cooldown': 30,
        })

    # پیدا کردن یا ساختن CareType
    try:
        care_type = CareType.objects.get(slug=qr.action_type, is_active=True)
    except CareType.DoesNotExist:
        _log_scan(qr, request, success=False, note='unknown care_type')
        return render(request, 'qrcodes/invalid.html', {
            'reason': 'نوع فعالیت تعریف نشده است',
            'qr': qr,
        }, status=400)

    # ثبت فعالیت
    log = CareLog.objects.create(
        plant=plant,
        care_type=care_type,
        performed_at=timezone.now(),
        source='qr',
        ip_address=ip,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        note='ثبت خودکار از طریق اسکن QR',
    )

    # به‌روزرسانی QR
    qr.scan_count += 1
    qr.last_scanned_at = timezone.now()
    qr.save(update_fields=['scan_count', 'last_scanned_at'])
    _log_scan(qr, request, note=f'log#{log.pk}')

    AuditLog.objects.create(
        user=None,
        action='action_qr_scan',
        model_name='CareLog',
        object_id=str(log.pk),
        metadata={
            'plant_id': plant.pk,
            'care_type': care_type.slug,
            'qr_token': qr.token[:8],
        },
        ip_address=ip,
    )

    return render(request, 'qrcodes/action_success.html', {
        'plant': plant,
        'qr': qr,
        'care_type': care_type,
        'log': log,
    })






@login_required
def print_qr(request, plant_pk):
    plant = get_object_or_404(Plant, pk=plant_pk, owner=request.user)
    qr_codes = plant.qr_codes.filter(status=QRCode.Status.ACTIVE)
    return render(request, 'qrcodes/print_qr.html', {
        'plant': plant,
        'qr_codes': qr_codes,
    })