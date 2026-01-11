from . import views
from django.urls import path, include

app_name = 'storage'

urlpatterns = [
    path('', views.home, name='storage_home'),
    path('map', views.storage_map, name='storage_map'),
    path('moviment', views.storage_movimentation, name='storage_movimentation'),
]