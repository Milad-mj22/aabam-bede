from django.db import migrations


CARE_TYPES = [
    {'name': 'آبیاری', 'slug': 'watering', 'icon': '💧', 'color': '#10b981'},
    {'name': 'کوددهی', 'slug': 'fertilizer', 'icon': '🌱', 'color': '#f59e0b'},
    {'name': 'دارو', 'slug': 'medicine', 'icon': '💊', 'color': '#ef4444'},
    {'name': 'سم‌پاشی', 'slug': 'pest_control', 'icon': '🐛', 'color': '#a855f7'},
    {'name': 'هرس', 'slug': 'pruning', 'icon': '✂️', 'color': '#0ea5e9'},
    {'name': 'تعویض گلدان', 'slug': 'repotting', 'icon': '🪴', 'color': '#84cc16'},
    {'name': 'اسپری برگ', 'slug': 'misting', 'icon': '🌫️', 'color': '#06b6d4'},
    {'name': 'بررسی سلامت', 'slug': 'inspection', 'icon': '🔍', 'color': '#f97316'},
]


def seed(apps, schema_editor):
    CareType = apps.get_model('care', 'CareType')
    for data in CARE_TYPES:
        CareType.objects.update_or_create(slug=data['slug'], defaults=data)


def unseed(apps, schema_editor):
    CareType = apps.get_model('care', 'CareType')
    CareType.objects.filter(slug__in=[d['slug'] for d in CARE_TYPES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('care', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed, unseed),
    ]