"""
URL configuration for PlantCare project.

مسیرهای اصلی پروژه:
- admin/         → پنل مدیریت Django
- accounts/      → احراز هویت (ثبت‌نام، ورود، خروج، بازیابی رمز)
- plants/        → مدیریت گیاهان (CRUD + گالری)
- care/          → برنامه‌ریزی و ثبت مراقبت
- qr/            → سیستم QR Code (Plant QR + Action QR)
- notifications/ → سیستم یادآوری و اطلاع‌رسانی
- /              → داشبورد اصلی (core)
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# --- تنظیمات پنل ادمین ---
admin.site.site_header = "پنل مدیریت PlantCare"
admin.site.site_title = "PlantCare Admin"
admin.site.index_title = "مدیریت سامانه هوشمند مراقبت از گیاهان"


urlpatterns = [
    # --- ادمین ---
    path('admin/', admin.site.urls),

    # --- اپ‌های اصلی ---
    path('', include('core.urls')),                    # داشبورد
    path('accounts/', include('accounts.urls')),       # احراز هویت
    path('plants/', include('plants.urls')),           # گیاهان
    path('care/', include('care.urls')),               # مراقبت
    path('qr/', include('qrcodes.urls')),              # QR Code
    path('notifications/', include('notifications.urls')),  # اطلاع‌رسانی

    # --- ریدایرکت‌های پیش‌فرض ---
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]


# --- سرو فایل‌های استاتیک و مدیا در حالت توسعه ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)