python manage.py shell
from django.contrib.sites.models import Site
Site.objects.update_or_create(
    pk=1,
    defaults={
        'domain': 'aabam-bede.ir',
        'name': 'آبم بده',
    }
)
exit()