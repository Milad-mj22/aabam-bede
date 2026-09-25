from django.urls import path
from . import views

app_name = 'care'

urlpatterns = [
    # برنامه‌های مراقبت
    path('plant/<int:plant_pk>/schedule/create/', views.ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedule/<int:pk>/edit/', views.ScheduleUpdateView.as_view(), name='schedule_update'),
    path('schedule/<int:pk>/delete/', views.ScheduleDeleteView.as_view(), name='schedule_delete'),

    # ثبت فعالیت‌ها
    path('plant/<int:plant_pk>/log/create/', views.CareLogCreateView.as_view(), name='log_create'),
    path('log/<int:pk>/delete/', views.CareLogDeleteView.as_view(), name='log_delete'),

    # تقویم
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
]