from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Notification


# ============================================================
#  List View
# ============================================================

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)

        # فیلتر بر اساس خوانده‌شده/نخوانده
        status = self.request.GET.get('status', '')
        if status == 'unread':
            qs = qs.filter(is_read=False)
        elif status == 'read':
            qs = qs.filter(is_read=True)

        # فیلتر بر اساس نوع
        ntype = self.request.GET.get('type', '')
        if ntype:
            qs = qs.filter(notification_type=ntype)

        return qs.select_related('plant')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        base_qs = Notification.objects.filter(user=self.request.user)
        ctx['total_count'] = base_qs.count()
        ctx['unread_count'] = base_qs.filter(is_read=False).count()
        ctx['read_count'] = base_qs.filter(is_read=True).count()
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['current_type'] = self.request.GET.get('type', '')
        ctx['type_choices'] = Notification.Type.choices
        return ctx


# ============================================================
#  Mark as read
# ============================================================

@login_required
@require_POST
def mark_as_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.mark_as_read()

    # اگر درخواست AJAX باشد
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'unread_count': Notification.objects.filter(
                user=request.user, is_read=False
            ).count(),
        })

    # اگر درخواست عادی باشد
    if notif.url:
        return redirect(notif.url)
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    from .services import mark_all_read as service_mark_all

    count = service_mark_all(request.user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'marked': count, 'unread_count': 0})

    return redirect('notifications:list')


# ============================================================
#  Unread count (AJAX)
# ============================================================

@login_required
def unread_count(request):
    count = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()
    return JsonResponse({'count': count})


# ============================================================
#  Recent (for navbar dropdown)
# ============================================================

@login_required
def recent_notifications(request):
    """۵ نوتیفیکیشن اخیر برای dropdown"""
    notifs = Notification.objects.filter(
        user=request.user
    ).select_related('plant')[:5]

    data = []
    for n in notifs:
        data.append({
            'id': n.pk,
            'title': n.title,
            'message': n.message[:80],
            'type': n.notification_type,
            'icon': n.icon,
            'url': n.url or '/notifications/',
            'is_read': n.is_read,
            'time_ago': n.time_ago,
            'priority_color': n.priority_color,
        })

    return JsonResponse({
        'notifications': data,
        'unread_count': Notification.objects.filter(
            user=request.user, is_read=False
        ).count(),
    })


# ============================================================
#  Delete notification
# ============================================================

@login_required
@require_POST
def delete_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})

    return redirect('notifications:list')