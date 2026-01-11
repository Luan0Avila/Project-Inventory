from django.shortcuts import render, redirect

from .models import Stock, Position
from django.db.models import Exists, OuterRef
from django.contrib import messages
from .forms import MovementForm

def home(request):
    return render(request, 'storage/pages/home.html')

def storage_map(request):
    positions = Position.objects.annotate(
        occupied=Exists(
            Stock.objects.filter(
                position=OuterRef('pk'),
                quantity__gt=0
            )
        )
    )

    return render(request, 'storage/pages/map.html', {
        'positions': positions
    }) 


def storage_movimentation(request):
    if request.method == 'POST':
        form = MovementForm(request.POST)
        if form.is_valid():
            movement = form.save()

            stock, created = Stock.objects.get_or_create(
                item=movement.item,
                position=movement.position,
                defaults={'quantity': 0}
            )

            if movement.movement_type == 'IN':
                stock.quantity += movement.quantity
            else:
                stock.quantity -= movement.quantity

            stock.save()

            messages.success(request, 'Movimentação realizada com sucesso!')
            return redirect('storage:storage_movimentation')
    else:
        form = MovementForm()

    return render(request, 'storage/pages/movement_form.html', {
        'form': form
    })