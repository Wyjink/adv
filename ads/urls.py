from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_ads, name='upload_ads'),
    path('ads/<str:location>/', views.get_ads_by_location, name='get_ads_by_location'),
]