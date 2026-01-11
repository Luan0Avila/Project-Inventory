from . import views
from django.urls import path, include

app_name = 'storage'

urlpatterns = [
    path('', views.home, name='storage_home'),
    path('map', views.storage_map, name='storage_map'),
    path('movement/', views.stock_movement, name='stock_movement'),
]