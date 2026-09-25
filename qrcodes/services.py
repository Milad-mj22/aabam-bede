import io
import qrcode
from django.core.files.base import ContentFile
from django.urls import reverse


def generate_qr_image(url: str) -> ContentFile:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name='qr.png')


from django.conf import settings
from django.urls import reverse


def build_plant_qr_url(request, token):
    """ساخت URL مطلق برای Plant QR"""
    path = reverse('qrcodes:public_plant', kwargs={'token': token})

    # استفاده از SITE_URL در production
    if not settings.DEBUG and settings.SITE_URL:
        return f"{settings.SITE_URL}{path}"

    # در توسعه، از request استفاده کن
    return request.build_absolute_uri(path)


def build_action_qr_url(request, token):
    """ساخت URL مطلق برای Action QR"""
    path = reverse('qrcodes:action', kwargs={'token': token})

    if not settings.DEBUG and settings.SITE_URL:
        return f"{settings.SITE_URL}{path}"

    return request.build_absolute_uri(path)