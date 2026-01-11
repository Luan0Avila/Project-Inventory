from django.shortcuts import render

from .models import Position

def home(request):
    return render(request, 'storage/pages/home.html')

def mapa_estoque(request):
    positions = Position.objects.all()
    return render(request, 'storage/pages/map.html', {'positions': positions})
