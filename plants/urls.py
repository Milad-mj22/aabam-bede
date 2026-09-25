from django.urls import path
from . import views

app_name = 'plants'

urlpatterns = [
    path('', views.PlantListView.as_view(), name='list'),
    path('create/', views.PlantCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PlantDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PlantUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.PlantDeleteView.as_view(), name='delete'),

    # عکس‌ها (بعداً پیاده می‌کنیم)
    path('<int:plant_pk>/photos/upload/', views.PlantPhotoUploadView.as_view(), name='photo_upload'),
    path('photos/<int:pk>/delete/', views.PlantPhotoDeleteView.as_view(), name='photo_delete'),
]