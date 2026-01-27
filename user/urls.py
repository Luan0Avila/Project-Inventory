from . import views
from django.urls import path, include

app_name = 'user'

urlpatterns = [
    path('register/', views.register_view, name='register_view' )
]
