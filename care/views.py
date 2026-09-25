import calendar as pycalendar
from datetime import date, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.utils import timezone
from plants.models import Plant
from .models import CareSchedule, CareLog, CareType
from .forms import CareScheduleForm, CareLogForm


# ------------------------------
# Schedule CRUD
# ------------------------------
class ScheduleCreateView(LoginRequiredMixin, CreateView):
    model = CareSchedule
    form_class = CareScheduleForm
    template_name = 'care/schedule_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.plant = get_object_or_404(Plant, pk=kwargs['plant_pk'], owner=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['plant'] = self.plant
        ctx['mode'] = 'create'
        return ctx

    def form_valid(self, form):
        form.instance.plant = self.plant
        messages.success(self.request, 'برنامه مراقبت ایجاد شد.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('plants:detail', kwargs={'pk': self.plant.pk})


class ScheduleUpdateView(LoginRequiredMixin, UpdateView):
    model = CareSchedule
    form_class = CareScheduleForm
    template_name = 'care/schedule_form.html'

    def get_queryset(self):
        return CareSchedule.objects.filter(plant__owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['plant'] = self.object.plant
        ctx['mode'] = 'update'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'برنامه به‌روزرسانی شد.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('plants:detail', kwargs={'pk': self.object.plant.pk})


class ScheduleDeleteView(LoginRequiredMixin, DeleteView):
    model = CareSchedule
    template_name = 'care/confirm_delete.html'

    def get_queryset(self):
        return CareSchedule.objects.filter(plant__owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['object_type'] = 'برنامه مراقبت'
        ctx['cancel_url'] = reverse_lazy('plants:detail', kwargs={'pk': self.object.plant.pk})
        return ctx

    def get_success_url(self):
        messages.warning(self.request, 'برنامه حذف شد.')
        return reverse_lazy('plants:detail', kwargs={'pk': self.object.plant.pk})


# ------------------------------
# CareLog CRUD
# ------------------------------
class CareLogCreateView(LoginRequiredMixin, CreateView):
    model = CareLog
    form_class = CareLogForm
    template_name = 'care/log_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.plant = get_object_or_404(Plant, pk=kwargs['plant_pk'], owner=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['plant'] = self.plant
        return ctx

    def get_initial(self):
        initial = super().get_initial()
        initial['performed_at'] = timezone.now()
        return initial

    def form_valid(self, form):
        form.instance.plant = self.plant
        form.instance.source = 'web'
        messages.success(self.request, 'فعالیت ثبت شد.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('plants:detail', kwargs={'pk': self.plant.pk})


class CareLogDeleteView(LoginRequiredMixin, DeleteView):
    model = CareLog
    template_name = 'care/confirm_delete.html'

    def get_queryset(self):
        return CareLog.objects.filter(plant__owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['object_type'] = 'فعالیت'
        ctx['cancel_url'] = reverse_lazy('plants:detail', kwargs={'pk': self.object.plant.pk})
        return ctx

    def get_success_url(self):
        messages.warning(self.request, 'فعالیت حذف شد.')
        return reverse_lazy('plants:detail', kwargs={'pk': self.object.plant.pk})


# ------------------------------
# Calendar View
# ------------------------------
class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'care/calendar.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        # ماه جاری یا از کوئری‌استرینگ
        today = timezone.now().date()
        try:
            year = int(self.request.GET.get('year', today.year))
            month = int(self.request.GET.get('month', today.month))
            if not (1 <= month <= 12):
                month = today.month
        except (ValueError, TypeError):
            year, month = today.year, today.month

        # ساختار تقویم
        cal = pycalendar.Calendar(firstweekday=5)  # شنبه = 5
        month_days = cal.monthdatescalendar(year, month)

        # برنامه‌های کاربر در این ماه
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)

        schedules = CareSchedule.objects.filter(
            plant__owner=user,
            is_active=True,
            start_date__lte=last_day,
        ).select_related('plant', 'care_type')

        logs = CareLog.objects.filter(
            plant__owner=user,
            performed_at__date__gte=first_day,
            performed_at__date__lte=last_day,
        ).select_related('plant', 'care_type')

        # نقشه‌گذاری رویدادها روی روزها
        events_by_day = {}

        for sched in schedules:
            current = max(sched.start_date, first_day)
            interval = max(sched.interval_days, 1)
            # پیدا کردن اولین روز همراستا با برنامه
            delta = (current - sched.start_date).days
            if delta % interval != 0:
                current += timedelta(days=(interval - delta % interval) % interval)

            while current <= last_day:
                if sched.end_date and current > sched.end_date:
                    break
                events_by_day.setdefault(current, []).append({
                    'type': 'schedule',
                    'title': f"{sched.care_type.name} — {sched.plant.name}",
                    'icon': sched.care_type.icon or '📌',
                    'color': sched.care_type.color or '#10b981',
                    'plant_id': sched.plant_id,
                })
                current += timedelta(days=interval)

        for log in logs:
            d = log.performed_at.date()
            events_by_day.setdefault(d, []).append({
                'type': 'log',
                'title': f"{log.care_type.name} — {log.plant.name}",
                'icon': log.care_type.icon or '✅',
                'color': log.care_type.color or '#0ea5e9',
                'plant_id': log.plant_id,
            })

        # دیکشنری نهایی برای قالب
        weeks_data = []
        for week in month_days:
            row = []
            for d in week:
                row.append({
                    'date': d,
                    'day': d.day,
                    'in_month': (d.month == month),
                    'is_today': (d == today),
                    'events': events_by_day.get(d, []),
                })
            weeks_data.append(row)

        # دکمه‌های ماه قبل/بعد
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        month_names = [
            '', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ]

        ctx.update({
            'weeks': weeks_data,
            'current_year': year,
            'current_month': month,
            'month_name': month_names[month] if 1 <= month <= 12 else '',
            'today': today,
            'prev_year': prev_year,
            'prev_month': prev_month,
            'next_year': next_year,
            'next_month': next_month,
            'weekday_names': ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه'],
        })
        return ctx