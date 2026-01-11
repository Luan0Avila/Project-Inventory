from . import views
from django.urls import path, include

app_name = 'storage'

urlpatterns = [
    path('', views.home, name='storage_home'),
    path('map', views.mapa_estoque, name='storage_map'),
]