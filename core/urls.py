from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'core'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/charts/', views.dashboard_charts, name='charts'),
    path(
        'robots.txt',
        TemplateView.as_view(template_name='robots.txt', content_type='text/plain'),
        name='robots',
    ),
    path(
        'sitemap.xml',
        TemplateView.as_view(template_name='sitemap.xml', content_type='application/xml'),
        name='sitemap',
    ),


]