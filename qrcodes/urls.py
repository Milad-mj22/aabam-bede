from django.urls import path
from . import views

app_name = 'qrcodes'

urlpatterns = [
    path('generate/plant/<int:plant_pk>/', views.generate_plant_qr, name='generate_plant'),
    path('generate/action/<int:plant_pk>/<str:action>/', views.generate_action_qr, name='generate_action'),
    path('revoke/<int:qr_pk>/', views.revoke_qr, name='revoke'),
    path('p/<str:token>/', views.public_plant, name='public_plant'),
    path('a/<str:token>/', views.action_qr, name='action'),
    path('print/<int:plant_pk>/', views.print_qr, name='print'),
]