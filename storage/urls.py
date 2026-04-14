from . import views
from django.urls import path, include

app_name = 'storage'

urlpatterns = [
    path('', views.home, name='storage_home'),
    path('map', views.storage_map, name='storage_map'),
    path('position/<int:position_id>/', views.position_detail, name='position_detail'),
    path('movement/', views.stock_movement, name='stock_movement'),
    path('stock/', views.stock_overview, name='stock_overview'),
    path('position/<int:position_id>/edit/', views.position_edit, name='position_edit'),
    path('history/', views.movement_history, name='history')

]