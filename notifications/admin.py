from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'notification_type',
        'priority', 'is_read', 'created_at',
    ]
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'
    list_per_page = 30
    actions = ['mark_as_read_action']

    @admin.action(description='علامت‌گذاری به‌عنوان خوانده‌شده')
    def mark_as_read_action(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} نوتیفیکیشن علامت‌گذاری شد.')